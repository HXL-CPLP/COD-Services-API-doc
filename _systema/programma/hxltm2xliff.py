#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  hxltm2xliff
#
#         USAGE:  hxltm2xliff schemam-un-htcds.tm.hxl.csv schemam-un-htcds.xliff
#                 cat schemam-un-htcds.tm.hxl.csv | hxltm2xliff > schemam-un-htcds.xliff
#
#   DESCRIPTION:  _[eng-Latn] hxltm2xliff is an working draft of a tool to
#                             convert prototype of translation memory stored
#                             with HXL to XLIFF v2.1
#                 [eng-Latn]_
#                 @see http://docs.oasis-open.org/xliff/xliff-core/v2.1/os/xliff-core-v2.1-os.html
#                 @see https://github.com/HXL-CPLP/forum/issues/58
#                 @see https://github.com/HXL-CPLP/Auxilium-Humanitarium-API/issues/16
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#                     - libhxl (@see https://pypi.org/project/libhxl/)
#                     - (disabled) hug (https://github.com/hugapi/hug/)
#                     - your-extra-python-lib-here
#                 - your-non-python-dependency-here
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Emerson Rocha <rocha[at]ieee.org>
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication
#                 SPDX-License-Identifier: Unlicense
#       VERSION:  v0.7
#       CREATED: 2021-06-27 19:50 UTC v0.5, de github.com/EticaAI
#                       /HXL-Data-Science-file-formats/blob/main/bin/hxl2example
#      REVISION:  2021-06-27 21:16 UTC v0.6 de hxl2tab
#      REVISION:  2021-06-27 23:53 UTC v0.7 --archivum-extensionem=.csv
# ==============================================================================

# Tests
# ./_systema/programma/hxltm2xliff.py --help
# ./_systema/programma/hxltm2xliff.py _hxltm/schemam-un-htcds.tm.hxl.csv
# ./_systema/programma/hxltm2xliff.py _hxltm/schemam-un-htcds-5items.tm.hxl.csv

__VERSION__ = "v0.7"

import sys
import os
import logging
import argparse

# @see https://github.com/HXLStandard/libhxl-python
#    pip3 install libhxl --upgrade
# Do not import hxl, to avoid circular imports
import hxl.converters
import hxl.filters
import hxl.io

import csv
import tempfile

# @see https://github.com/hugapi/hug
#     pip3 install hug --upgrade
# import hug

# In Python2, sys.stdin is a byte stream; in Python3, it's a text stream
STDIN = sys.stdin.buffer

# for line in hxl.data(sys.stdin).gen_csv():
# for line in hxl.data('_hxltm/schemam-un-htcds-5items.tm.hxl.csv', allow_local=True).gen_csv():
# for line in hxl.data('_hxltm/schemam-un-htcds-5items.tm.hxl.csv', allow_local=True).with_rows('#sector=WASH').gen_csv():
# for line in hxl.data('_hxltm/schemam-un-htcds-5items.tm.hxl.csv', allow_local=True).without_columns('#meta').gen_csv():
#     print('ooooi', line)


class HXLTM2XLIFF:
    """
    _[eng-Latn] hxltm2xliff is an working draft of a tool to
                convert prototype of translation memory stored with HXL to
                XLIFF v2.1
    [eng-Latn]_
    """

    def __init__(self):
        """
        _[eng-Latn] Constructs all the necessary attributes for the
                    HXLTM2XLIFF object.
        [eng-Latn]_
        """
        self.hxlhelper = None
        self.args = None

        # Posix exit codes
        self.EXIT_OK = 0
        self.EXIT_ERROR = 1
        self.EXIT_SYNTAX = 2

        self.original_outfile = None
        self.original_outfile_is_stdout = True

    def make_args_hxl2example(self):

        self.hxlhelper = HXLUtils()
        parser = self.hxlhelper.make_args(
            #     description=("""
            # _[eng-Latn] hxltm2xliff is an working draft of a tool to
            #             convert prototype of translation memory stored with HXL to
            #             XLIFF v2.1
            # [eng-Latn]_
            # """)
            description=(
                "_[eng-Latn] hxltm2xliff " + __VERSION__ + " " +
                "is an working draft of a tool to " +
                "convert prototype of translation memory stored with HXL to " +
                "XLIFF v2.1 [eng-Latn]_"
            )
        )

        parser.add_argument(
            '--archivum-extensionem',
            help='File extension. .xlf or .csv',
            action='store',
            default='.xlf',
            nargs='?'
        )

        parser.add_argument(
            '--fontem-linguam',
            help='Source language (use if not autodetected). ' +
            'Must be like {ISO 639-3}-{ISO 15924}. Example: por-Latn',
            action='store',
            default='lat-Latn',
            nargs='?'
        )

        parser.add_argument(
            '--objectivum-linguam',
            help='XLiff Target language (use if not autodetected). ' +
            'Must be like {ISO 639-3}-{ISO 15924}. Example: eng-Latn',
            action='store',
            default='arb-Arab',
            nargs='?'
        )

        parser.add_argument(
            "--hxlmeta",
            help="Don't print output, just the hxlmeta of the input",
            action='store_const',
            const=True,
            metavar='hxlmeta',
            default=False
        )

        self.args = parser.parse_args()
        return self.args

    def execute_cli(self, args,
                    stdin=STDIN, stdout=sys.stdout, stderr=sys.stderr):
        """
        The execute_cli is the main entrypoint of HXLTM2XLIFF. When
        called will convert the HXL source to example format.
        """

        # # NOTE: the next lines, in fact, only generate an csv outut. So you
        # #       can use as starting point.
        # with self.hxlhelper.make_source(args, stdin) as source, \
        #         self.hxlhelper.make_output(args, stdout) as output:
        #     hxl.io.write_hxl(output.output, source,
        #                      show_tags=not args.strip_tags)

        # return self.EXIT_OK

        # If the user specified an output file, we will save on
        # self.original_outfile. The args.outfile will be used for temporary
        # output
        if args.outfile:
            self.original_outfile = args.outfile
            self.original_outfile_is_stdout = False

        try:
            temp = tempfile.NamedTemporaryFile()
            args.outfile = temp.name

            with self.hxlhelper.make_source(args, stdin) as source, \
                    self.hxlhelper.make_output(args, stdout) as output:
                source.without_columns('#meta')
                source.with_columns('#item')

                # print(source)

                hxl.io.write_hxl(output.output, source,
                                 show_tags=not args.strip_tags)

            if args.hxlmeta:
                print('TODO: hxlmeta')
                # print('output.output', output.output)
                # print('source', source)
                # # print('source.columns', source.headers())
                # hxlmeta = HXLMeta(local_hxl_file=output.output.name)
                # hxlmeta.debuginfo()
            elif args.archivum_extensionem == '.csv':
                # print('CSV!')
                self.hxltm2csv(args.outfile, self.original_outfile,
                               self.original_outfile_is_stdout, args)
            else:
                self.hxl2tab(args.outfile, self.original_outfile,
                             self.original_outfile_is_stdout, args)

        finally:
            temp.close()

        return self.EXIT_OK

    def hxltm2csv(self, hxlated_input, tab_output, is_stdout, args):
        """
        hxl2tab is  is the main method to de facto make the conversion.
        """

        with open(hxlated_input, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Hotfix: skip first non-HXL header. Ideally I think the already
            # exported HXlated file should already save without headers.
            next(csv_reader)
            header_original = next(csv_reader)
            header_new = self.hxltm2csv_header(
                header_original,
                fontem_linguam=args.fontem_linguam,
                objectivum_linguam=args.objectivum_linguam,
            )

            if is_stdout:
                # txt_writer = csv.writer(sys.stdout, delimiter='\t')
                txt_writer = csv.writer(sys.stdout)
                txt_writer.writerow(header_new)
                for line in csv_reader:
                    txt_writer.writerow(line)
            else:

                tab_output_cleanup = open(tab_output, 'w')
                tab_output_cleanup.truncate()
                tab_output_cleanup.close()

                with open(tab_output, 'a') as new_txt:
                    # txt_writer = csv.writer(new_txt, delimiter='\t')
                    txt_writer = csv.writer(new_txt)
                    txt_writer.writerow(header_new)
                    for line in csv_reader:
                        txt_writer.writerow(line)

    def hxl2tab(self, hxlated_input, tab_output, is_stdout, args):
        """
        hxl2tab is  is the main method to de facto make the conversion.
        """

        with open(hxlated_input, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Hotfix: skip first non-HXL header. Ideally I think the already
            # exported HXlated file should already save without headers.
            next(csv_reader)
            header_original = next(csv_reader)
            header_new = self.hxltm2csv_header(
                header_original,
                fontem_linguam=args.fontem_linguam,
                objectivum_linguam=args.objectivum_linguam,
            )

            if is_stdout:
                txt_writer = csv.writer(sys.stdout, delimiter='\t')
                txt_writer.writerow(header_new)
                for line in csv_reader:
                    txt_writer.writerow(line)
            else:

                tab_output_cleanup = open(tab_output, 'w')
                tab_output_cleanup.truncate()
                tab_output_cleanup.close()

                with open(tab_output, 'a') as new_txt:
                    txt_writer = csv.writer(new_txt, delimiter='\t')
                    txt_writer.writerow(header_new)
                    for line in csv_reader:
                        txt_writer.writerow(line)

    # def hxl2tab_header(self, hxlated_header):
    def hxltm2csv_header(self, hxlated_header, fontem_linguam, objectivum_linguam):
        """
        _[eng-Latn] Convert the Main HXL TM file to a single or source to target
                    XLIFF translation pair
        [eng-Latn]_

#item+id                               -> #x_xliff+unit+id
#meta+archivum                         -> #x_xliff+file

    [contextum: XLIFF srcLang]
#item(*)+i_ZZZ+is_ZZZZ                 -> #x_xliff+source+i_ZZZ+is_ZZZZ
#status(*)+i_ZZZ+is_ZZZZ+xliff         -> #meta+x_xliff+segment_source+state+i_ZZZ+is_ZZZZ (XLIFF don't support)

    [contextum: XLIFF trgLang]
#item(*)+i_ZZZ+is_ZZZZ                 -> #x_xliff+target+i_ZZZ+is_ZZZZ
#status(*)+i_ZZZ+is_ZZZZ+xliff         -> #x_xliff+segment+state+i_ZZZ+is_ZZZZ
        """

        # TODO: improve this block. I'm very sure there is some cleaner way to
        #       do it in a more cleaner way (fititnt, 2021-01-28 08:56 UTC)

        # NOTE: +vt_orange_type_continuous (but not +number),
        #       +vt_orange_type_string (but not +text, +name)
        #       etc are replaced from the end result
        #       In other words: the very specific data types don't need to be
        #       added to the end result, but we keep generic ones to avoid
        #       potentially break other tools.

        fon_ling = HXLTM2XLIFF.linguam_2_hxlattrs(fontem_linguam)
        obj_ling = HXLTM2XLIFF.linguam_2_hxlattrs(objectivum_linguam)

        # print('fon_ling', fon_ling)
        # print('obj_ling', obj_ling)

        for idx, _ in enumerate(hxlated_header):

            # feature types
            if hxlated_header[idx] == '#item+id':
                hxlated_header[idx] = '#x_xliff+unit+id'
                continue

            elif hxlated_header[idx] == '#meta+archivum':
                hxlated_header[idx] = '#x_xliff+file'
                continue

            elif hxlated_header[idx].startswith('#item'):

                if hxlated_header[idx].find(fon_ling) > -1 and \
                        not hxlated_header[idx].find('+list') > -1:
                    hxlated_header[idx] = '#x_xliff+source' + fon_ling
                elif hxlated_header[idx].find(obj_ling) > -1 and \
                        not hxlated_header[idx].find('+list') > -1:
                    hxlated_header[idx] = '#x_xliff+target' + obj_ling

                continue

            elif hxlated_header[idx].startswith('#status'):
                if hxlated_header[idx].find(fon_ling) > -1 and \
                        not hxlated_header[idx].find('+list') > -1:
                    # TODO: maybe just ignore source state? XLIFF do not
                    #       support translations from source languages that
                    #       are not ideally ready yet
                    if hxlated_header[idx].find('+xliff') > -1:
                        hxlated_header[idx] = '#x_xliff+segment+state' + fon_ling
                elif hxlated_header[idx].find(obj_ling) > -1 and \
                        not hxlated_header[idx].find('+list') > -1:
                    if hxlated_header[idx].find('+xliff') > -1:
                        hxlated_header[idx] = '#x_xliff+segment+state' + obj_ling
                if hxlated_header[idx] != '#status':
                    print('#status ERROR?, FIX ME', hxlated_header[idx])
                continue

            elif hxlated_header[idx].startswith('#meta'):
                continue
                # print('TODO')
            # elif True:
            #     break
            # elif hxlated_header[idx].find('+vt_orange_type_discrete') > -1 \
            #         or hxlated_header[idx].find('+vt_categorical') > -1:

            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_orange_type_discrete', '')
            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_categorical', '')
            #     hxlated_header[idx] = 'D' + hxlated_header[idx]

            # elif hxlated_header[idx].find('+vt_orange_type_continuous') > -1 \
            #         or hxlated_header[idx].find('+number') > -1:

            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_orange_type_discrete', '')
            #     hxlated_header[idx] = 'C' + hxlated_header[idx]
            # elif hxlated_header[idx].find('+vt_orange_type_string') > -1 or \
            #         hxlated_header[idx].find('+text') > -1 or \
            #         hxlated_header[idx].find('+name') > -1:

            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_orange_type_string', '')
            #     hxlated_header[idx] = 'S' + hxlated_header[idx]

            # # optional flags
            # if hxlated_header[idx].find('+vt_orange_flag_class') > -1 or \
            #         hxlated_header[idx].find('+vt_class') > -1:

            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_orange_flag_class', '')
            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_class', '')
            #     hxlated_header[idx] = 'c' + hxlated_header[idx]

            # elif hxlated_header[idx].find('+vt_orange_flag_meta') > -1 or \
            #         hxlated_header[idx].find('+vt_meta') > -1 or \
            #         hxlated_header[idx].find('#meta') > -1:

            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_orange_flag_meta', '')
            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_meta', '')
            #     hxlated_header[idx] = 'm' + hxlated_header[idx]

            # elif hxlated_header[idx].find('+vt_orange_flag_ignore') > -1:

            #     hxlated_header[idx] = hxlated_header[idx].replace(
            #         '+vt_orange_flag_ignore', '')
            #     hxlated_header[idx] = 'i' + hxlated_header[idx]

        # print('hxl2tab_header', hxlated_header)
        return hxlated_header

    # def execute_web(self, source_url, stdin=STDIN, stdout=sys.stdout,
    #                 stderr=sys.stderr, hxlmeta=False):
    #     """
    #     The execute_web is the main entrypoint of HXL2Tab when this class is
    #     called outside command line interface, like the build in HTTP use with
    #     hug
    #     """

    #     # TODO: the execute_web needs to output the tabfile with correct
    #     #       mimetype, compression, etc
    #     #       (fititnt, 2021-02-07 15:59 UTC)

    #     self.hxlhelper = HXLUtils()

    #     try:
    #         temp_input = tempfile.NamedTemporaryFile('w')
    #         temp_output = tempfile.NamedTemporaryFile('w')

    #         webargs = type('obj', (object,), {
    #             "infile": source_url,
    #             "sheet_index": None,
    #             "selector": None,
    #             'sheet': None,
    #             'http_header': None,
    #             'ignore_certs': False
    #         })

    #         with self.hxlhelper.make_source(webargs, stdin) as source:
    #             for line in source.gen_csv(True, True):
    #                 temp_input.write(line)

    #             temp_input.seek(0)
    #             # self.hxl2tab(temp_input.name, temp_output.name, False)

    #             result_file = open(temp_input.name, 'r')
    #             return result_file.read()

    #     finally:
    #         temp_input.close()
    #         temp_output.close()

    #     return self.EXIT_OK

    def linguam_2_hxlattrs(linguam):
        """linguam_2_hxlattrs

        Example:
            >>> HXLTM2XLIFF.linguam_2_hxlattrs('por-Latn')
            +i_por+is_latn
            >>> HXLTM2XLIFF.linguam_2_hxlattrs('arb-Arab')
            +i_arb+is_Arab

        Args:
            linguam ([String]): A linguam code

        Returns:
            [String]: HXL Attributes
        """
        iso6393, iso115924 = list(linguam.lower().split('-'))
        return '+i_' + iso6393 + '+is_' + iso115924


class HXLUtils:
    """
    HXLUtils contains functions from the Console scripts of libhxl-python
    (HXLStandard/libhxl-python/blob/master/hxl/scripts.py) with few changes
    to be used as class (and have one single place to change).
    Last update on this class was 2021-01-25.

    Author: David Megginson
    License: Public Domain
    """

    def __init__(self):

        self.logger = logging.getLogger(__name__)

        # Posix exit codes
        self.EXIT_OK = 0
        self.EXIT_ERROR = 1
        self.EXIT_SYNTAX = 2

    def make_args(self, description, hxl_output=True):
        """Set up parser with default arguments.
        @param description: usage description to show
        @param hxl_output: if True (default), include options for HXL output.
        @returns: an argument parser, partly set up.
        """
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            'infile',
            help='HXL file to read (if omitted, use standard input).',
            nargs='?'
        )
        if hxl_output:
            parser.add_argument(
                'outfile',
                help='HXL file to write (if omitted, use standard output).',
                nargs='?'
            )
        parser.add_argument(
            '--sheet',
            help='Select sheet from a workbook (1 is first sheet)',
            metavar='number',
            type=int,
            nargs='?'
        )
        parser.add_argument(
            '--selector',
            help='JSONPath expression for starting point in JSON input',
            metavar='path',
            nargs='?'
        )
        parser.add_argument(
            '--http-header',
            help='Custom HTTP header to send with request',
            metavar='header',
            action='append'
        )
        if hxl_output:
            parser.add_argument(
                '--remove-headers',
                help='Strip text headers from the CSV output',
                action='store_const',
                const=True,
                default=False
            )
            parser.add_argument(
                '--strip-tags',
                help='Strip HXL tags from the CSV output',
                action='store_const',
                const=True,
                default=False
            )
        parser.add_argument(
            "--ignore-certs",
            help="Don't verify SSL connections (useful for self-signed)",
            action='store_const',
            const=True,
            default=False
        )
        parser.add_argument(
            '--log',
            help='Set minimum logging level',
            metavar='debug|info|warning|error|critical|none',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            default='error'
        )
        return parser

    def add_queries_arg(
        self,
        parser,
        help='Apply only to rows matching at least one query.'
    ):
        parser.add_argument(
            '-q',
            '--query',
            help=help,
            metavar='<tagspec><op><value>',
            action='append'
        )
        return parser

    def do_common_args(self, args):
        """Process standard args"""
        logging.basicConfig(
            format='%(levelname)s (%(name)s): %(message)s',
            level=args.log.upper())

    def make_source(self, args, stdin=STDIN):
        """Create a HXL input source."""

        # construct the input object
        input = self.make_input(args, stdin)
        return hxl.io.data(input)

    def make_input(self, args, stdin=sys.stdin, url_or_filename=None):
        """Create an input object"""

        if url_or_filename is None:
            url_or_filename = args.infile

        # sheet index
        sheet_index = args.sheet
        if sheet_index is not None:
            sheet_index -= 1

        # JSONPath selector
        selector = args.selector

        http_headers = self.make_headers(args)

        return hxl.io.make_input(
            url_or_filename or stdin,
            sheet_index=sheet_index,
            selector=selector,
            allow_local=True,  # TODO: consider change this for execute_web
            http_headers=http_headers,
            verify_ssl=(not args.ignore_certs)
        )

    def make_output(self, args, stdout=sys.stdout):
        """Create an output stream."""
        if args.outfile:
            return FileOutput(args.outfile)
        else:
            return StreamOutput(stdout)

    def make_headers(self, args):
        # get custom headers
        header_strings = []
        header = os.environ.get("HXL_HTTP_HEADER")
        if header is not None:
            header_strings.append(header)
        if args.http_header is not None:
            header_strings += args.http_header
        http_headers = {}
        for header in header_strings:
            parts = header.partition(':')
            http_headers[parts[0].strip()] = parts[2].strip()
        return http_headers


class FileOutput(object):
    """
    FileOutput contains is based on libhxl-python with no changes..
    Last update on this class was 2021-01-25.

    Author: David Megginson
    License: Public Domain
    """

    def __init__(self, filename):
        self.output = open(filename, 'w')

    def __enter__(self):
        return self

    def __exit__(self, value, type, traceback):
        self.output.close()


class StreamOutput(object):
    """
    StreamOutput contains is based on libhxl-python with no changes..
    Last update on this class was 2021-01-25.

    Author: David Megginson
    License: Public Domain
    """

    def __init__(self, output):
        self.output = output

    def __enter__(self):
        return self

    def __exit__(self, value, type, traceback):
        pass

    def write(self, s):
        self.output.write(s)


if __name__ == "__main__":

    hxltm2xliff = HXLTM2XLIFF()
    args = hxltm2xliff.make_args_hxl2example()

    hxltm2xliff.execute_cli(args)


# @hug.format.content_type('text/csv')
# def output_csv(data, response):
#     if isinstance(data, dict) and 'errors' in data:
#         response.content_type = 'application/json'
#         return hug.output_format.json(data)
#     response.content_type = 'text/csv'
#     if hasattr(data, "read"):
#         return data

#     return str(data).encode("utf8")


# @hug.get('/hxltm2xliff.csv', output=output_csv)
# def api_hxl2example(source_url):
#     """hxltm2xliff (@see https://github.com/EticaAI/HXL-Data-Science-file-formats)

#     Example:
#     http://localhost:8000/hxltm2xliff.csv?source_url=https://docs.google.com/spreadsheets/u/1/d/1l7POf1WPfzgJb-ks4JM86akFSvaZOhAUWqafSJsm3Y4/edit#gid=634938833

#     """

#     hxltm2xliff = HXLTM2XLIFF()

#     return hxltm2xliff.execute_web(source_url)
