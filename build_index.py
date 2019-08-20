import click

from charity import CharityIndex


@click.command()
@click.argument('source-csv')
@click.argument('output-dir')
def main(source_csv, output_dir):
    index = CharityIndex.build_from_csv(source_csv)
    index.save(output_dir)


if __name__ == '__main__':
    main()
