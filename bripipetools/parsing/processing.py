import logging
import datetime
import os
import re

logger = logging.getLogger(__name__)


def parse_batch_name(batch_name):
    """
    Parse batch name indicated in workflow batch submit file and
    return individual components indicating date, list of project
    labels, and flowcell ID.
    """
    name_parts = batch_name.split('_')
    date = datetime.datetime.strptime(name_parts.pop(0), '%y%m%d')

    fc_id = name_parts.pop(-1)

    return {'date': date, 'projects': name_parts, 'flowcell_id': fc_id}


def parse_workflow_param(param):
    """
    Parse workflow parameter into components indicating tag,
    type, and name.
    """
    param_tag = param.split('##')[0]
    if re.search('annotation', param_tag):
        param_type = 'annotation'
    elif re.search('in$', param_tag):
        param_type = 'input'
    elif re.search('out$', param_tag):
        param_type = 'output'
    else:
        param_type = 'sample'

    return {'tag': param_tag,
            'type': param_type,
            'name': param.split('::')[-1]}


def parse_output_name(output_name):
    output_name_short = re.sub('_out$', '', output_name)
    if re.search('trimmed_fastq', output_name_short):
        output_name_short = re.sub('trimmed', 'fastqmcf_trimmed',
                                   output_name_short)

    if re.search('^trinity_fasta', output_name_short):
        output_name_short = re.sub('trinity', 'trinity_trinity',
                                   output_name_short)

    name_parts = output_name_short.split('_')
    logger.debug("output name has following parts: {}".format(name_parts))

    output_ext = name_parts.pop(-1)
    output_type = name_parts.pop(-1)
    if re.search('-', output_type):
        output_type, output_subtype = output_type.split('-')
        output_label = '-'.join([output_type, output_subtype])
    else:
        output_label = output_type

    try:
        source = name_parts.pop(-1)
    except IndexError:
        logging.exception("output name '{}' appears to be invalid"
                          .format(output_name))
        raise

    if len(name_parts):
        source = '-'.join([name_parts.pop(-1), source])

    return {'type': output_type,
            'label': output_label,
            'source': source,
            'extension': output_ext}


def parse_output_filename(output_path):
    """
    Parse output name indicated by parameter tag in output file
    return individual components indicating processed library ID,
    output source, and type.
    """
    output_filename = os.path.basename(output_path)
    output_name = os.path.splitext(output_filename)[0]
    name_parts = output_name.split('_')

    output_type = name_parts.pop(-1)
    source = name_parts.pop(-1)
    if (len(name_parts) <= 2
        and not re.search('(picard|tophat)', name_parts[-1])):
        sample_id = '_'.join(name_parts)
    else:
        source = '-'.join([name_parts.pop(-1), source])
        sample_id = '_'.join(name_parts)

    return {'sample_id': sample_id, 'type': output_type,
            'source': source}
