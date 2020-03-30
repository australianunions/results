from logx import log
from sqlbag import create_database  # noqa
from sqlbag.pg import use_pendulum_for_time_types  # noqa

from .cleaning import standardize_key, standardized_key_mapping  # noqa
from .connections import db  # noqa
from .fileutil import file_text, files, from_file, from_files  # noqa
from .openers import (  # noqa
    csv_column_names,
    csv_rows_it,
    detect_enc,
    detect_string_enc,
    dicts_from_rows,
    first_n_lines,
    from_csv,
    from_psv,
    from_tsv,
    from_xls,
    from_xlsx,
    smart_open,
    sniff_csv_dialect,
)
from .resources import (  # noqa
    resource_data,
    resource_path,
    resource_stream,
    resource_text,
)
from .result import Result  # noqa
from .resultset import Results  # noqa
from .saving import save_xlsx  # noqa
from .sqlutil import create_table_statement  # noqa
from .typeguess import (  # noqa
    guess_column_type,
    guess_sql_column_type,
    guess_value_type,
)
from .util import noneslarger, nonessmaller, trunc  # noqa
from .uuids import deterministic_uuid  # noqa

log.set_null_handler()
use_pendulum_for_time_types()
