import sys, json

def main(argv):
    param_file = sys.argv[1]

    result_type_dict = {#'FASTQ Trimmer': 'trimmedFastq',
                        'FastqMcf: log': 'adapterTrimMetrics',
                        #'FastqMcf: reads': 'trimmedFastq',
                        'FASTQ Quality Trimmer': 'trimmedFastq',
                        'FastQC: html': 'fastqQc',
                        'Tophat for Illumina: insertions': 'inBedFile',
                        'Tophat for Illumina: deletions': 'delBedFile',
                        'Tophat for Illumina: splice junctions': 'juncBedFile',
                        'Tophat for Illumina: accepted_hits': 'bamFile',
                        'MarkDups: bam': 'rmDupBamFile',
                        'MarkDups: html': 'rmDupMetrics',
                        'Picard Alignment Summary Metrics.html': 'alignMetrics',
                        'RNA Seq Metrics.html': 'rnaseqMetrics',
                        'Tophat Stats PE': 'tophatStatsMetrics',
                        'htseq-count': 'countFile',
                        'htseq-count (no feature)': 'htseqMetrics',
                        'MACS2 callpeak (Bedgraph Treatment)': 'macsTreatBedFile',
                        'MACS2 callpeak (Bedgraph Control)': 'macsCtrlBedFile',
                        'MACS2 callpeak (Peaks in BED format)': 'macsPeaksBedFile',
                        'MACS2 callpeak (html report)': 'macsReport',
                        'MACS2 callpeak (summits in BED)': 'macsSummitsBedFile',
                        'MTDupsFilterStats': 'atacSeqMetrics'}

    folder_dict = {'adapterTrimMetrics': 'metrics',
                  'trimmedFastq': 'TrimmedFastqs',
                  'fastqQc': 'QC',
                  'inBedFile': 'viz',
                  'delBedFile': 'viz',
                  'juncBedFile': 'viz',
                  'bamFile': 'alignments',
                  'rmDupBamFile': 'alignments_noDups',
                  'rmDupMetrics': 'metrics',
                  'alignMetrics': 'metrics',
                  'rnaseqMetrics': 'metrics',
                  'tophatStatsMetrics': 'metrics',
                  'countFile': 'counts',
                  'htseqMetrics': 'metrics',
                  'macsTreatBedFile': 'peakCallOutput',
                  'macsCtrlBedFile': 'peakCallOutput',
                  'macsPeaksBedFile': 'peakCallOutput',
                  'macsReport': 'peakCallOutput',
                  'macsSummitsBedFile': 'peakCallOutput',
                  'atacSeqMetrics': 'metrics'}

    ext_dict = {'adapterTrimMetrics': '_fqmcf.txt',
               'trimmedFastq': '_trimmed.fastq',
               'fastqQc': '_qc.zip',
               'inBedFile': '_insertions.bed',
               'delBedFile': '_deletions.bed',
               'juncBedFile': '_junctions.bed',
               'bamFile': '.bam',
               'rmDupBamFile': '_noDups.bam',
               'rmDupMetrics': 'MarkDups.zip',
               'alignMetrics': '_al.zip',
               'rnaseqMetrics': '_qc.zip',
               'tophatStatsMetrics': 'ths.txt',
               'countFile': '_count.txt',
               'htseqMetrics': 'mm.txt',
               'macsTreatBedFile': '_treatment.bed',
               'macsCtrlBedFile': '_control.bed',
               'macsPeaksBedFile': '_peaks.bed',
               'macsReport': '_report.zip',
               'macsSummitsBedFile': '_summits.bed',
               'atacSeqMetrics': '_atac.zip'}

    method_dict = {'.txt': 'remote',
                  '.zip': 'remote',
                  '.fastq': 'local',
                  '.bam': 'local',
                  '.bed': 'local'}

    params = {'result_types': result_type_dict,
              'folders': folder_dict,
              'extensions': ext_dict,
              'methods': method_dict}

    with open(param_file, 'wb+') as f:
        json.dump(params, f)

if __name__ == "__main__":
   main(sys.argv[1:])
