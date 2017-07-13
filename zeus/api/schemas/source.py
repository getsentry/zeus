from marshmallow import Schema, fields, pre_dump

from .revision import RevisionSchema


class SourceSummarySchema(Schema):
    id = fields.UUID(dump_only=True)
    revision = fields.Nested(RevisionSchema())
    created_at = fields.DateTime(attribute="date_created", dump_only=True)


class SourceSchema(Schema):
    id = fields.UUID(dump_only=True)
    revision = fields.Nested(RevisionSchema())
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    diff = fields.Str(dump_only=True)

    @pre_dump
    def process_diff(self, data):
        return data.generate_diff()


# diff = source.generate_diff()

# if diff:
#     files = self._get_files_from_raw_diff(diff)

#     coverage = {
#         c.filename: c.data
#         for c in get_coverage_by_source_id(source_id)
#         if c.filename in files
#     }

#     coverage_for_added_lines = self._filter_coverage_for_added_lines(
#         diff, coverage)

#     tails_info = dict(source.data)
# else:
#     coverage = None
#     coverage_for_added_lines = None
#     tails_info = None

# context['diff'] = diff
# context['coverage'] = coverage
# context['coverageForAddedLines'] = coverage_for_added_lines
# context['tailsInfo'] = tails_info

# def _filter_coverage_for_added_lines(self, diff, coverage):
#     """
#     This function takes a diff (text based) and a map of file names to the coverage for those files and
#     returns an ordered list of the coverage for each "addition" line in the diff.

#     If we don't have coverage for a specific file, we just mark the lines in those files as unknown or 'N'.
#     """
#     if not diff:
#         return None

#     # Let's just encode it as utf-8 just in case
#     diff_lines = diff.encode('utf-8').splitlines()

#     current_file = None
#     line_number = None
#     coverage_by_added_line = []

#     for line in diff_lines:
#         if line.startswith('diff'):
#             # We're about to start a new file.
#             current_file = None
#             line_number = None
#         elif current_file is None and line_number is None and (
#                 line.startswith('+++') or line.startswith('---')):
#             # We're starting a new file
#             if line.startswith('+++ b/'):
#                 line = line.split('\t')[0]
#                 current_file = unicode(line[6:])
#         elif line.startswith('@@'):
#             # Jump to new lines within the file
#             line_num_info = line.split('+')[1]
#             line_number = int(line_num_info.split(',')[0]) - 1
#         elif current_file is not None and line_number is not None:
#             # Iterate through the file.
#             if line.startswith('+'):
#                 # Make sure we have coverage for this line.  Else just tag it as unknown.
#                 cov = 'N'
#                 if current_file in coverage:
#                     try:
#                         cov = coverage[current_file][line_number]
#                     except IndexError:
#                         logger = logging.getLogger('coverage')
#                         logger.info(
#                             'Missing code coverage for line %d of file %s'
#                             % (line_number, current_file))

#                 coverage_by_added_line.append(cov)

#             if not line.startswith('-'):
#                 # Up the line count (assuming we aren't at a remove line)
#                 line_number += 1

#     return coverage_by_added_line

# def _get_files_from_raw_diff(self, diff):
#     """
#     Returns a list of filenames from a diff.
#     """
#     files = set()
#     diff_lines = diff.encode('utf-8').split('\n')
#     for line in diff_lines:
#         if line.startswith('+++ b/'):
#             line = line.split('\t')[0]
#             files.add(unicode(line[6:]))

#     return files
