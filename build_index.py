import click

from charity import CharityIndex


@click.command()
@click.argument('source-tsv')
@click.argument('output-dir')
def main(source_tsv, output_dir):
    index = CharityIndex.build_from_tsv(source_tsv)
    index.save(output_dir)


if __name__ == '__main__':
    main()
