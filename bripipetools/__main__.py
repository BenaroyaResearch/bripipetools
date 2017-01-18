import logging
import os
import re
import sys

import click

import bripipetools

logging.basicConfig()
logger = logging.getLogger(__name__)


def get_workflow_batches(flowcell_path):
    submissions = os.path.join(flowcell_path, 'globus_batch_submission')
    return (os.path.join(submissions, wb)
            for wb in os.listdir(submissions)
            if 'optimized' in wb)


def get_processed_projects(flowcell_path):
    return (os.path.join(flowcell_path, pp)
            for pp in os.listdir(flowcell_path)
            if re.search('Project_.*Processed', pp))


def postprocess_project(output_type, exclude_types, stitch_only, clean_outputs, 
                        project_path):
    project_path_short = os.path.basename(os.path.normpath(project_path))
    if clean_outputs:
        logging.info("cleaning output files for '{}'"
                     .format(project_path))
        bripipetools.postprocess.OutputCleaner(project_path).clean_outputs()

    logger.info("combining output files for '{}' with option '{}'"
                .format(project_path_short, output_type))

    combined_paths = []
    if output_type in ['c', 'a'] and 'c' not in exclude_types:
        logger.info("generating combined counts file")
        path = os.path.join(project_path, 'counts')
        bripipetools.postprocess.OutputStitcher(path).write_table()

    if output_type in ['m', 'a'] and 'm' not in exclude_types:
        logger.info("generating combined metrics file")
        path = os.path.join(project_path, 'metrics')
        combined_paths.append(
            bripipetools.postprocess.OutputStitcher(path).write_table())

    if output_type in ['q', 'a'] and 'q' not in exclude_types:
        logger.info("generating combined QC file(s)")
        path = os.path.join(project_path, 'QC')
        bripipetools.postprocess.OutputStitcher(
            path).write_overrepresented_seq_table()
        combined_paths.append(
            bripipetools.postprocess.OutputStitcher(path).write_table())

    if output_type in ['v', 'a'] and 'v' not in exclude_types:
        logger.info("generating combined validation file(s)")
        path = os.path.join(project_path, 'validation')
    try:
        combined_paths.append(
            bripipetools.postprocess.OutputStitcher(path).write_table()
        )
    except OSError:
        logger.warn(("no validation files found "
                     "for project {}; skiproject_pathing").format(project_path))

    if not stitch_only:
        logger.info("merging all combined summary data tables")
        bripipetools.postprocess.OutputCompiler(combined_paths).write_table()


@click.group()
def cli():
    logger.setLevel(logging.INFO)
    logger.info("starting `bripipetools`")


@click.command()
@click.option('--print-opt')
def test(print_opt):
    click.echo("Hello World! {}".format(print_opt))


@click.command()
@click.option('--endpoint', default='jeddy#srvgridftp01')
@click.option('--workflow-dir', default='/mnt/genomics/galaxy_workflows')
@click.argument('path')
def submit(endpoint, workflow_dir, path):
    submitter = bripipetools.submission.FlowcellSubmissionBuilder(
        path=path,
        endpoint=endpoint,
        db=bripipetools.genlims.db,
        workflow_dir=workflow_dir
    )
    submit_paths = submitter.run()
    for p in submit_paths:
        print(p)


@click.command()
@click.argument('path')
def dbify(path):
    logger.info("importing data based on path {}"
                .format(path))
    importer = bripipetools.dbify.ImportManager(
        path=path,
        db=bripipetools.genlims.db
    )
    importer.run()


@click.command()
@click.option('--output-type', '-t', default='a',
              type=click.Choice(['c', 'm', 'q', 'v', 'a']))
@click.option('--exclude-types', '-x', multiple=True,
              type=click.Choice(['c', 'm', 'q', 'v']))
@click.option('--stitch-only/--stitch-and-compile', default=False)
@click.option('--clean-outputs/--outputs-as-is', default=False)
@click.argument('path')
def postprocess(output_type, exclude_types, stitch_only, clean_outputs, path):
    postprocess_project(output_type, exclude_types, stitch_only,
                        clean_outputs, path)


@click.command()
@click.option('--output-type', '-t', default='a',
              type=click.Choice(['c', 'm', 'q', 'v', 'a']))
@click.option('--exclude-types', '-x', multiple=True,
              type=click.Choice(['c', 'm', 'q', 'v']))
@click.option('--stitch-only/--stitch-and-compile', default=False)
@click.option('--clean-outputs/--outputs-as-is', default=False)
@click.argument('path')
def wrapup(output_type, exclude_types, stitch_only, clean_outputs, path):
    # import flowcell run details and raw data for sequenced libraries
    logger.info("importing raw data for flowcell at path {}"
                .format(path))
    importer = bripipetools.dbify.ImportManager(
        path=path,
        db=bripipetools.genlims.db
    )
    importer.run()

    workflow_batches = list(get_workflow_batches(path))
    logger.info("found the following workflow batches: {}"
                .format(workflow_batches))

    # check outputs of workflow batches
    genomics_root = bripipetools.util.matchdefault('.*(?=genomics)', path)
    problem_count = 0
    for wb in workflow_batches:
        logger.info("checking outputs for workflow batch in file '{}'"
                    .format(wb))
        wb_outputs = bripipetools.monitoring.WorkflowBatchMonitor(
            workflowbatch_file=wb, genomics_root=genomics_root
        ).check_outputs()

        problem_outputs = filter(lambda x: x[1]['status'] != 'ok',
                                 wb_outputs.items())
        problem_count += len(problem_outputs)
        if len(problem_outputs):
            output_warnings = map(lambda x: 'OUTPUT {}: {}'.format(
                x[1]['status'].upper(), x[0]
            ), problem_outputs)
            for w in output_warnings:
                logger.warning(w)

    # give option to continue
    if problem_count > 0:
        proceed = raw_input("{} problems encountered; proceed? (y/[n]): "
                            .format(problem_count))
        if proceed != 'y':
            logger.info("exiting program")
            sys.exit(1)
    else:
        logger.info("no problem outputs found")

    # import workflow batch details and data for processed libraries
    for wb in workflow_batches:
        logger.info(
            "importing processed data for workflow batch in file '{}'"
            .format(wb))
        bripipetools.dbify.ImportManager(
            path=wb,
            db=bripipetools.genlims.db
        ).run()

    processed_projects = list(get_processed_projects(path))
    logger.info("found the following processed projects: {}"
                .format(processed_projects))

    # post-process project files
    for pp in processed_projects:
        postprocess_project(output_type, exclude_types, stitch_only,
                            clean_outputs, pp)


cli.add_command(test)
cli.add_command(submit)
cli.add_command(dbify)
cli.add_command(postprocess)
cli.add_command(wrapup)

if __name__ == "__main__":
    cli()
