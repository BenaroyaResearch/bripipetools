import logging
import os
import re

import mock
import mongomock
import pytest

from bripipetools import annotation
from bripipetools import submission

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def mock_db():
    # GIVEN a mock_ed version of the TG3 Mongo database
    logger.info(("[setup] mock_ database, connect "
                 "to mock Mongo database"))

    yield mongomock.MongoClient().db
    logger.debug(("[teardown] mock_ database, disconnect "
                  "from mock Mongo database"))


@pytest.fixture(scope='function')
def mock_params():
    yield [{'tag': 'SampleName', 'type': 'sample', 'name': 'SampleName'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_endpoint'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_path4'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_path5'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_path6'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_path7'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_path1'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_path2'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_path3'},
           {'tag': 'fastq_in', 'type': 'input', 'name': 'from_path8'},
           {'tag': 'annotation_gtf', 'type': 'annotation', 'name': 'gtfFile'},
           {'tag': 'annotation_adapters', 'type': 'annotation', 'name': 'adapterFile'},
           {'tag': 'annotation_ribosomal_intervals', 'type': 'annotation', 'name': 'ribointsFile'},
           {'tag': 'annotation_refflat', 'type': 'annotation', 'name': 'refflatFile'},
           {'tag': 'tophat_alignments_bam_out', 'type': 'output', 'name': 'to_endpoint'},
           {'tag': 'tophat_alignments_bam_out', 'type': 'output', 'name': 'to_path'}]


class TestBatchParameterizer:
    """

    """
    def test_get_lane_order(self, mock_params):
        # mock_filename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        # mock_file = mock_template(mock_filename, tmpdir)
        mock_paths = ['lib1111-11111111', 'lib2222-22222222']

        parameterizer = submission.BatchParameterizer(
            sample_paths=mock_paths,
            parameters=mock_params,
            endpoint='',
            target_dir=''
        )

        logger.debug("{}".format(parameterizer.parameters))
        assert (parameterizer._get_lane_order()
                == ['4', '5', '6', '7', '1', '2', '3', '8'])

    def test_get_lane_fastq_when_lane_exists(self, mock_params, tmpdir):
        mock_path = tmpdir.mkdir('lib1111-11111111')
        mock_lane = '2'
        mock_fastqpath = mock_path.ensure(
            'sample-name_S001_L00{}_R1_001.fastq.gz'.format(mock_lane)
        )

        parameterizer = submission.BatchParameterizer(
            sample_paths=[],
            parameters=mock_params,
            endpoint='',
            target_dir=''
        )

        test_fastqpath = parameterizer._get_lane_fastq(str(mock_path), mock_lane)

        assert (test_fastqpath == mock_fastqpath)

    def test_get_lane_fastq_when_lane_missing(self, mock_params, tmpdir):
        mock_path = tmpdir.mkdir('lib1111-11111111')
        mock_lane = '2'
        mock_path.ensure('sample-name_S001_L001_R1_001.fastq.gz')
        mock_fastqpath = mock_path.join('empty_L00{}.fastq.gz'
                                        .format(mock_lane))

        parameterizer = submission.BatchParameterizer(
            sample_paths=[],
            parameters=mock_params,
            endpoint='',
            target_dir=''
        )

        test_fastqpath = parameterizer._get_lane_fastq(str(mock_path), mock_lane)

        assert (test_fastqpath == mock_fastqpath)

    def test_build_reference_path(self, mock_params):
        parameterizer = submission.BatchParameterizer(
            sample_paths=[],
            parameters=mock_params,
            endpoint='',
            target_dir=''
        )

        mock_param = {'tag': 'annotation_gtf',
                      'type': 'annotation',
                      'name': 'gtfFile'}

        test_path = parameterizer._build_reference_path(mock_param)

        mock_path = 'library::annotation::GRCh38/Homo_sapiens.GRCh38.77.gtf'
        assert (test_path == mock_path)

    def test_prep_output_dir(self, mock_params, tmpdir):
        parameterizer = submission.BatchParameterizer(
            sample_paths=[],
            parameters=mock_params,
            endpoint='',
            target_dir=str(tmpdir)
        )

        mock_outtype = 'counts'
        mock_path = tmpdir.join(mock_outtype)

        test_path = parameterizer._prep_output_dir(mock_outtype)

        assert (test_path == mock_path)
        assert (os.path.exists(test_path))
        assert (os.path.isdir(test_path))

    def test_build_output_path(self, mock_params, tmpdir):
        mock_targetdir = tmpdir.mkdir('genomics')

        parameterizer = submission.BatchParameterizer(
            sample_paths=[],
            parameters=mock_params,
            endpoint='',
            target_dir=str(mock_targetdir)
        )

        mock_sample = 'lib1111_C00000XX'
        mock_param = {'tag': 'tophat_alignments_bam_out',
                      'type': 'output',
                      'name': 'to_path'}

        test_path = parameterizer._build_output_path(mock_sample, mock_param)

        mock_path = os.path.join('/mnt/genomics/alignments',
                                 'lib1111_C00000XX_tophat_alignments.bam')
        assert (test_path == mock_path)

    def test_build_sample_parameters(self, mock_params, tmpdir):
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('genomics').mkdir(mock_runid)
                     .mkdir('lib1111-11111111'))
        mock_fastqpath = mock_path.ensure(
            'sample-name_S001_L001_R1_001.fastq.gz'
        )
        mock_fastqpath = re.sub(str(tmpdir), '/mnt', str(mock_fastqpath))
        mock_emptypaths = {
            lane: re.sub(
                str(tmpdir), '/mnt', str(mock_path.join(
                    'empty_L00{}.fastq.gz'.format(lane))
                )
            )
            for lane in range(2, 9)
            }

        mock_endpoint = 'jeddy#srvgridftp01'
        mock_targetdir = (tmpdir.join('genomics').join(mock_runid))

        parameterizer = submission.BatchParameterizer(
            sample_paths=[str(mock_path)],
            parameters=mock_params,
            endpoint=mock_endpoint,
            target_dir=str(mock_targetdir)
        )

        test_values = parameterizer._build_sample_parameters(str(mock_path))

        mock_refpaths = [
            'library::annotation::GRCh38/Homo_sapiens.GRCh38.77.gtf',
            'library::annotation::adapters/smarter_adapter_seqs_3p_5p.fasta',
            ('library::annotation::GRCh38/Homo_sapiens.GRCh38.77'
             '.ribosomalIntervalsWheader_reorder.txt'),
            'library::annotation::GRCh38/Homo_sapiens.GRCh38.77.refflat.txt',
        ]

        mock_samplename = 'lib1111_C00000XX'
        mock_outpath = os.path.join(
            '/mnt/genomics/', mock_runid,
            'alignments', 'lib1111_C00000XX_tophat_alignments.bam'
        )
        mock_values = ([mock_samplename,
                        mock_endpoint, mock_emptypaths[4], mock_emptypaths[5],
                        mock_emptypaths[6], mock_emptypaths[7],
                        mock_fastqpath, mock_emptypaths[2], mock_emptypaths[3],
                        mock_emptypaths[8]]
                       + mock_refpaths
                       + [mock_endpoint, mock_outpath])
        assert (test_values == mock_values)

    def test_parameterize(self, mock_params, tmpdir):
        tmpdir = tmpdir.mkdir('genomics')
        mock_paths = [str(tmpdir.mkdir('lib1111-11111111')),
                      str(tmpdir.mkdir('lib2222-22222222'))]

        parameterizer = submission.BatchParameterizer(
            sample_paths=mock_paths,
            parameters=mock_params,
            endpoint='',
            target_dir=str(tmpdir)
        )

        parameterizer.parameterize()
        test_params = parameterizer.samples

        assert (len(test_params) == len(mock_paths))
        assert (test_params[0][0]
                == {'tag': 'SampleName',
                    'type': 'sample',
                    'name': 'SampleName',
                    'value': 'lib1111'})


@pytest.fixture(scope='function')
def mock_template(filename, tmpdir):
    # GIVEN a simplified workflow batch content with protypical contents
    mock_params = ['SampleName',
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_endpoint'),
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_path4'),
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_path5'),
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_path6'),
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_path7'),
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_path1'),
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_path2'),
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_path3'),
                   ('fastq_in##Param::2942::'
                    'globus_get_data_flowcell_text::from_path8'),
                   'annotation_gtf##SourceType::SourceName::gtfFile',
                   'annotation_adapters##SourceType::SourceName::adapterFile',
                   ('annotation_ribosomal_intervals##SourceType::'
                    'SourceName::ribointsFile'),
                   'annotation_refflat##SourceType::SourceName::refflatFile',
                   ('tophat_alignments_bam_out##Param::2946::'
                    'globus_send_data::to_endpoint'),
                   ('tophat_alignments_bam_out##Param::2946::'
                    'globus_send_data::to_path')]

    mock_contents = ['###METADATA\n',
                     '#############\n',
                     'Workflow Name\toptimized_workflow_1\n',
                     'Workflow id\tba1f5a6a3d5eec2c\n',
                     'Project Name\t<Your_project_name>\n',
                     '###TABLE DATA\n',
                     '#############\n',
                     '{}\n'.format('\t'.join(mock_params))]
    mock_file = tmpdir.join(filename)
    mock_file.write(''.join(mock_contents))
    return str(mock_file)




class TestFlowcellSubmissionBuilder:
    """

    """
    def test_init_annotator(self, mock_db):
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = '/mnt/genomics/Illumina/{}'.format(mock_runid)
        mock_endpoint = 'jeddy#srvgridftp01'

        builder = submission.FlowcellSubmissionBuilder(
            path=mock_path,
            endpoint=mock_endpoint,
            db=mock_db
        )

        builder._init_annotator()

        assert (type(builder.annotator == annotation.FlowcellRunAnnotator))

    def test_get_workflow_options_for_all_workflows(self, mock_db, tmpdir):
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = '/mnt/genomics/Illumina/{}'.format(mock_runid)
        mock_endpoint = 'jeddy#srvgridftp01'

        mock_workflowdir = tmpdir.mkdir('galaxy_workflows')
        mock_workflows = ['workflow1.txt', 'optimized_workflow1.txt']
        mock_workflowopts = [str(mock_workflowdir.mkdir(w))
                             for w in mock_workflows]
        mock_workflowopts.sort()

        builder = submission.FlowcellSubmissionBuilder(
            path=mock_path,
            endpoint=mock_endpoint,
            db=mock_db,
            workflow_dir=str(mock_workflowdir)
        )

        test_workflowopts = builder.get_workflow_options(optimized_only=False)

        assert (test_workflowopts == mock_workflowopts)

    def test_get_workflow_options_for_optimized_workflows(self, mock_db,
                                                          tmpdir):
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = '/mnt/genomics/Illumina/{}'.format(mock_runid)
        mock_endpoint = 'jeddy#srvgridftp01'

        mock_workflowdir = tmpdir.mkdir('galaxy_workflows')
        mock_workflows = ['workflow1.txt', 'optimized_workflow1.txt']
        mock_workflowopts = [str(mock_workflowdir.mkdir(w))
                             for w in mock_workflows
                             if re.search('optimized', w)]
        mock_workflowopts.sort()

        builder = submission.FlowcellSubmissionBuilder(
            path=mock_path,
            endpoint=mock_endpoint,
            db=mock_db,
            workflow_dir=str(mock_workflowdir)
        )

        test_workflowopts = builder.get_workflow_options()

        assert (test_workflowopts == mock_workflowopts)

    def test_get_projects(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_endpoint = 'jeddy#srvgridftp01'

        # AND the unaligned folder includes multiple project folders
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_path = tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mock_runid)
        mock_unaligndir = mock_path.mkdir('Unaligned')
        mock_paths = [mock_unaligndir.mkdir(p) for p in mock_projects]

        builder = submission.FlowcellSubmissionBuilder(
            path=str(mock_path),
            endpoint=mock_endpoint,
            db=mock_db
        )

        builder._get_project_paths()

        assert (builder.project_paths == mock_paths)

