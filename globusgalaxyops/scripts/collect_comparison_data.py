import os, sys, re, zipfile, csv
from pprint import pprint
from bs4 import BeautifulSoup
import pysam
from Bio import SeqIO
import pandas as pd

class MetricsCollector(object):

    def __init__(self, metrics_dir):

        self.dir = metrics_dir

    def get_metrics_list(self):

        self.ml = [ os.path.join(self.dir, f) \
                    for f in os.listdir(self.dir) \
                    if not re.search('^\.', f)]


    def parse_picard_html(self, html_doc, source='table'):
        soup = BeautifulSoup(html_doc, 'html.parser')
        table = soup.findAll('table', attrs={'cellpadding': '3'})

        metric_dict = {}

        if len(table):
            if source == 'table':
                for tr in table[0].findAll('tr'):
                    for td in tr.findAll('td'):
                        if re.search('^([A-Z]+(\_)*)+$', td.text):
                            td_key = td.text.replace('\n', '')
                            td_val = td.next_sibling.string.replace(u'\xa0', u'')
                            td_val = td_val.replace('\n', '')
                            if not re.search('[a-z]', td_val.lower()) and len(td_val):
                                td_val = float(td_val)
                                metric_dict[td_key] = td_val
            elif source == 'cell':
                for tr in table[0].findAll('tr'):
                    for td in tr.findAll('td'):
                        if re.search('^[A-Z]+', td.text):
                            td_keys = td.text.split('\t')
                            td_vals = tr.next_sibling.next_sibling.text.split('\t')
                            td_keys = td_keys[0:len(td_vals)]
                            metric_dict = { key: float(td_vals[idx]) for idx,key in enumerate(td_keys) }
        else:
            print html_doc


        return metric_dict

    def read_picard(self, metrics_file):
        zfile = zipfile.ZipFile(metrics_file)
        metric_html = [ f for f in zfile.namelist() if 'html' in f ][0]
        if 'rna_seq' in metric_html.lower():
            source = 'cell'
        else:
            source = 'table'

        with zfile.open(metric_html) as f:
            html_doc = f.read()
            metric_dict = self.parse_picard_html(html_doc, source)
        return metric_dict

    def parse_text(self, metric_lines, source=None):
        if source == 'htseq':
            metric_dict = { l.split('\t')[0].lstrip('__'): \
                            float(l.split('\t')[1].strip()) \
                            for l in metric_lines }

        elif source == 'tophat':
            metric_dict = { re.sub(' ', '_', l.split('\t')[1].strip()): \
                            l.split('\t')[0] \
                            for l in metric_lines }
            for m in metric_dict:
                val = metric_dict[m]
                if type(val) == str and re.search('%', val):
                    new_val = float(re.search('[0-9]+(\.[0-9]+)*', val).group()) / 100
                    key = 'perc_' + m
                    metric_dict[key] = new_val
                    del(metric_dict[m])
                else:
                    metric_dict[m] = float(val)

        return metric_dict

    def read_text(self, metrics_file):
        if 'mm' in metrics_file:
            source = 'htseq'
        else:
            source = 'tophat'

        with open(metrics_file, 'r') as f:
            metric_lines = f.readlines()
            metric_dict = self.parse_text(metric_lines, source)

        return metric_dict

    def build_metric_df(self):

        if not hasattr(self, 'ml'):
            self.get_metrics_list()

        lib_metric_dict = {}
        for f in self.ml:

            if not 'combined' in f:
                metrics_file = os.path.join(self.dir, f)

                lib = re.search('lib[0-9]+', metrics_file).group()

                if 'zip' in metrics_file:
                    metrics_dict = self.read_picard(metrics_file)
                else:
                    metrics_dict = self.read_text(metrics_file)

                if lib in lib_metric_dict:
                    lib_metric_dict[lib].update(metrics_dict)
                else:
                    lib_metric_dict[lib] = metrics_dict

        metric_df = pd.DataFrame(lib_metric_dict).transpose()
        self.mdf = metric_df

    def write_metric_df(self, out_path):
        print "Saving outputs..."

        if not hasattr(self, 'mdf'):
            self.build_metric_df()

        out_path += '_metrics.csv'

        self.mdf.to_csv(out_path)

class CountsCollector(object):
    def __init__(self, counts_dir):

        self.dir = counts_dir

    def get_counts_list(self):

        self.cl = [ os.path.join(self.dir, f) \
                    for f in os.listdir(self.dir) \
                    if not re.search('^\.', f) ]

    def get_lib_id(self, lib_file):
        lib_id = re.search('lib[0-9]+(.*(XX)+)*', lib_file).group()

        return lib_id

    def build_count_dict(self):

        if not hasattr(self, 'cl'):
            self.get_counts_list()

        count_dict = {}
        for idx,f in enumerate(self.cl):

            if not 'combined' in f:
                lib = self.get_lib_id(f)

                with open(f) as cf:
                    reader = csv.reader(cf, delimiter = '\t')
                    if idx == 0:
                        count_header = ['geneName', lib]
                        for row in reader:
                            count_dict[row[0]] = [row[1]]
                    else:
                        count_header.append(lib)
                        for row in reader:
                            count_dict[row[0]].append(row[1])

        self.lcd = count_dict
        self.lch = count_header


    def write_count_dict(self, out_path):
        print "Saving outputs..."

        if not hasattr(self, 'lcd'):
            self.build_count_dict()

        out_path += '_counts.csv'

        with open(out_path, 'w') as cf:
            writer = csv.writer(cf)
            writer.writerow(self.lch)
            for entry in self.lcd:
                writer.writerow([entry] + self.lcd[entry])

class FileStatsCollector(object):
    def __init__(self, proj_dir):

        self.dir = proj_dir

    def get_counts_list(self):

        self.cl = [ os.path.join(self.dir, f) \
                    for f in os.listdir(self.dir) \
                    if not re.search('^\.', f) ]


    def get_file_list(self, file_tag):

        file_tag += '$'
        file_list = [ os.path.join(dp, f) \
                      for dp,dn,fn in os.walk(self.dir) \
                      for f in fn \
                      if re.search(file_tag, f)]
        return file_list

    def get_lib_id(self, lib_file):
        lib_id = re.search('lib[0-9]+(.*(XX)+)*', lib_file).group()

        return lib_id

    def bufcount(self, filename):
        f = open(filename)
        lines = 0
        buf_size = 1024 * 1024
        read_f = f.read # loop optimization

        buf = read_f(buf_size)
        while buf:
            lines += buf.count('\n')
            buf = read_f(buf_size)

        return lines

    def get_size(self, filename):
        file_size = os.stat(filename).st_size

        return file_size

    def count_bam_records(self, bam_file):
        bam_records = list(pysam.AlignmentFile(bam_file, 'rb'))

        return len(bam_records)

    def count_fasta_records(self, fasta_file):
        handle = open(fasta_file, "rU")
        fasta_records = list(SeqIO.parse(handle, "fasta"))
        handle.close()

        return len(fasta_records)

    def count_fastq_records(self, fastq_file):
        handle = open(fastq_file, "rU")
        fastq_records = list(SeqIO.parse(handle, "fastq"))
        handle.close()

        return len(fastq_records)

    def build_file_stat_dict(self):

        file_type_list = ['fasta', 'fastq', 'bam']

        file_stat_dict = {}
        for ft in file_type_list:
            print "\n > Inspecting %s files" % ft

            file_list = self.get_file_list(ft)
            file_list = [ f for f in file_list if 'noDups' not in f ]

            for idx,f in enumerate(file_list):
                print "   file %d of %d:" % (idx + 1, len(file_list))

                if not 'combined' in f:
                    lib = self.get_lib_id(f)

                    if not lib in file_stat_dict:
                        file_stat_dict[lib] = {}

                    print "   (counting lines)"
                    file_stat_dict[lib][ft + '_lines'] = self.bufcount(f)

                    print "   (calculating file size)"
                    file_stat_dict[lib][ft + '_size'] = self.get_size(f)

                    print "   (counting records)"
                    if ft == 'bam':
                        file_stat_dict[lib][ft + '_records'] = self.count_bam_records(f)

                    elif ft == 'fasta':
                        file_stat_dict[lib][ft + '_records'] = self.count_fasta_records(f)

                    elif ft == 'fastq':
                        file_stat_dict[lib][ft + '_records'] = \
                        file_stat_dict[lib][ft + '_lines'] / 4


        self.fsd = file_stat_dict


    def write_file_stat_dict(self, out_path):
        print "Saving outputs..."

        if not hasattr(self, 'fsd'):
            self.build_file_stat_dict()

        out_path += '_file_stats.csv'

        pd.DataFrame(self.fsd).transpose().to_csv(out_path)

def collect_project_info(project_dir, out_dir, source, info='all'):
    project = re.search('P[0-9]+\-[0-9]+', project_dir).group()

    out_tag = project + '_' + source
    out_path = os.path.join(out_dir, out_tag)

    if info == 'all' or info == 'm':
        print "\nCollecting metrics info...\n"
        metrics_dir = os.path.join(os.path.abspath(project_dir), 'metrics')
        mc = MetricsCollector(metrics_dir)
        mc.write_metric_df(out_path)

    if info == 'all' or info == 'c':
        print "\nCollecting counts info...\n"
        counts_dir = os.path.join(os.path.abspath(project_dir), 'counts')
        cc = CountsCollector(counts_dir)
        cc.write_count_dict(out_path)

    if info == 'all' or info == 'f':
        print "\nCollecting file stats info...\n"
        fsc = FileStatsCollector(project_dir)
        fsc.write_file_stat_dict(out_path)

def main(argv):
    project_dir = sys.argv[1]
    out_dir = sys.argv[2]
    source = sys.argv[3]
    if len(sys.argv) > 4:
        info = sys.argv[4]
    else:
        info = 'all'

    collect_project_info(project_dir, out_dir, source, info)

if __name__ == "__main__":
   main(sys.argv[1:])
