import logging
logger = logging.getLogger(__name__)
import os
import sys
import zipfile
import math
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import lxml.html as lh
from datetime import datetime as dt


def read_rnaseq_metrics(path):
    try:
        logger.debug("unzipping contents for {}".format(path))
        zfile = zipfile.ZipFile(path)
        try:
            metrics_file = zfile.open('CollectRnaSeqMetrics.metrics.txt')
        except KeyError:
            metrics_file = zfile.open('RNA_Seq_Metrics_html.html')
        return metrics_file.readlines()
    except:
        logger.warning("not a zip file; reading lines directly")
        with open(path) as f:
            return f.readlines()

def get_norm_cov(rnaseq_metrics_lines):
    logger.debug("parsing normalized coverage histogram")
    try:
        logger.debug("attempting to parse histogram from "
                     "expected location (lines 11-112)")
        cov_hist_lines = rnaseq_metrics_lines[11:112]
        norm_cov = [float(line.rstrip('\n').split('\t')[-1])
                    for line in cov_hist_lines]
    except ValueError:
        try:
            logger.warning("parsing failed; attempting to parse histogram from "
                        "alternative location (lines 31-132)")
            cov_hist_lines = rnaseq_metrics_lines[31:132]
            norm_cov = [float(re.search('[0-9]*\t[0-9]+(\.[0-9]+)*', line)
                              .group()
                              .split('\t')[-1])
                        for line in cov_hist_lines]
        # THIS IS A HACK-Y WORKAROUND. NEED TO PARSE TABLE BETTER
        except AttributeError:
            try:
                logger.warning("parsing failed; attempting to parse histogram from "
                            "alternative location (lines 30-131)")
                cov_hist_lines = rnaseq_metrics_lines[30:131]
                norm_cov = [float(re.search('[0-9]*\t[0-9]+(\.[0-9]+)*', line)
                                  .group()
                                  .split('\t')[-1])
                            for line in cov_hist_lines]
            except AttributeError:
                logger.warning("no coverage histogram found, returning empty list")
                norm_cov = []
    return norm_cov
    
# def scrape_norm_cov_table(path):
#     lh.parse(path)

def build_norm_cov_df(metrics_path):
    rnaseq_metrics_files = [os.path.join(metrics_path, f)
                            for f in os.listdir(metrics_path)
                            if re.search('_al.zip', f)
                            or re.search('rnaseq_metrics.html', f)]
    rnaseq_metrics_files.sort()
    logger.info("found Picard RNA-seq metrics files for {} samples"
                .format(len(rnaseq_metrics_files)))

    norm_cov_dict = {}
    for f in rnaseq_metrics_files:
        logger.debug("reading RNA-seq metrics from {}".format(f))
        rnaseq_metrics_lines = read_rnaseq_metrics(f)
        norm_cov = get_norm_cov(rnaseq_metrics_lines)
        norm_cov = [0] * 101 if not len(norm_cov) else norm_cov

        logger.debug("parsing filename to get sample ID")
        lib = ('_').join(os.path.basename(f).split('_')[0:2])

        norm_cov_dict[lib] = norm_cov

    return pd.DataFrame(data=norm_cov_dict)

def build_metrics_df(metrics_path):
    logger.info("reading combined metrics file")
    combined_metrics_file = [f for f in os.listdir(metrics_path)
                             if 'combined_metrics.csv' in f][0]

    return pd.read_csv(os.path.join(metrics_path, combined_metrics_file))

def build_figure(ncDf, metDf, project, fc, outFolder):
    logger.info("building combined figure")
    with plt.style.context(('ggplot')):
        fig = plt.figure()

        plt.rcParams.update({'axes.titlesize':'medium'})

        numRows = int(math.ceil(float(len(ncDf.columns)) / 3))
        figHeight = numRows*2 + 1
        plotMargin = float(figHeight - 1) / float(figHeight)

        textHeight = (1 - plotMargin) / 2 + plotMargin

        fig.suptitle(('Normalized coverage vs. normalized transcript position\n'
                      'Project %s\n'
                      'Flowcell: %s' % (project, fc)),
                     x=0.02, y=textHeight, fontsize=11,
                     horizontalalignment='left', verticalalignment='center')

        fig.text(0.93, textHeight, '*libID_fcID [median_cv_coverage]',
                 fontsize=10, fontstyle='italic',
                 horizontalalignment='right', verticalalignment='center')

        colorList = plt.cm.hot(np.linspace(0, 0.5, 200))

        for idx, lib in enumerate(ncDf):
            logger.debug("creating subplot for {}".format(lib))
            try:
                logger.debug("locating sample metrics by field 'libId'")
                libIdx = metDf.libId == lib
            except AttributeError:
                logger.warning("failed; locating sample metrics by field 'libID'")
                libIdx = metDf.libID == lib
            mcc = float(metDf[libIdx]['median_cv_coverage'])
            fqReads = int(metDf[libIdx]['fastq_total_reads'])
            # Handle read pairs and unpaired reads, in case of PE alignment.
            percAligned = (float(metDf[libIdx]['unpaired_reads_examined']) + \
                          float(metDf[libIdx]['read_pairs_examined'])) / \
                          float(metDf[libIdx]['fastq_total_reads'])* 100

            mccColorIdx = min(int(mcc * 100), 200)
            ymax = max(ncDf[lib].max() + 0.1, 1.0)

            ax_i = fig.add_subplot(numRows, 3, idx + 1)
            ncDf[lib].plot(color=[colorList[mccColorIdx - 1],0,0],
                         ax=ax_i, xlim=(-5,105), ylim=(0,ymax))

            ax_i.text(100, 0.1, ('FASTQ reads: %s\n'
                               '%% aligned: %4.1f' % (fqReads, percAligned)),
                    bbox={'facecolor':'white', 'edgecolor':'grey',
                          'alpha':0.75, 'pad':10},
                    fontsize=9, horizontalalignment='right')

            ax_i.get_xaxis().tick_bottom()
            ax_i.get_yaxis().tick_left()

            ax_i.set_title('%s [%1.2f]' % (lib, mcc))
            ax_i.set_facecolor('white')
            
        # pull out fc id from full run string
        fcid_regex = re.compile( "(([A-Z0-9])*X(X|Y|2|3|F))|(000000000-C[A-Z0-9]{4})|(A[0-9a-zA-Z]+(M5|HV))")
        fcid =  fcid_regex.search(fc).group()

        fig.set_size_inches(7.5, figHeight)
        fig.tight_layout(rect=(0, 0, 1, plotMargin))
        fig.savefig(outFolder + project + '_' + fcid + '_' + dt.now().strftime('%y%m%d') + '_' + 'geneModelCoverage.pdf',
              format = "pdf")

def main(argv):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    metrics_path = argv[0]

    out_path = metrics_path

    path_parts = re.split("/", metrics_path)
    try:
        project_regex = re.compile('P+[0-9]+(-[0-9]+){,1}')
        #project = project_regex.search(path_parts[5]).group()
        project = project_regex.search(metrics_path).group()
        #flowcell_id = path_parts[4]
        flowcell_regex = re.compile('[0-9]{6}_[A-Z0-9]+_[0-9]+_(([A-Z0-9])*X(X|Y|2|3|F))|(000000000-C[A-Z0-9]{4})|(000000000-C[A-Z0-9]{4})|(A[0-9a-zA-Z]+(M5|HV))')
        flowcell_id =  flowcell_regex.search(metrics_path).group()
    except AttributeError:
        project = re.sub('Processed.*', '', path_parts[4].lstrip('Project_'))
        flowcell_id = path_parts[3]

    print("Metrics path: " + metrics_path)
    print("Project: " + project)
    print("Flow cell ID: " + flowcell_id)
    norm_cov_df = build_norm_cov_df(metrics_path)
    metrics_df = build_metrics_df(metrics_path)
    build_figure(norm_cov_df, metrics_df, project, flowcell_id, out_path)

if __name__ == "__main__":
   main(sys.argv[1:])
