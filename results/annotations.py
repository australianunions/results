from decimal import Decimal
from decimal import InvalidOperation as InvalidOp
from numbers import Number


class AnnotationsMixin:
    def annotate_histogram_amplitudes(self):
        def is_numeric(x):
            return isinstance(x, Number) and not isinstance(x, bool)

        for k in self.keys():
            col = self[k]
            filtered = [_ for _ in col if is_numeric(_)]

            if not filtered:
                continue

            _min = min(filtered)
            _max = max(filtered)
            min0 = min(_min, 0.0)
            max0 = max(0.0, _max)
            _range = Decimal(max0) - Decimal(min0)

            _subclasses_by_type = {}

            for r in self:
                v = r[k]

                if not is_numeric(v):
                    continue

                v0, v1 = sorted([0.0, v])

                try:
                    d = Decimal(v0) - Decimal(min0)
                    start = Decimal(d) / Decimal(_range)
                    h0 = float(start)
                except InvalidOp:
                    h0 = 0.0

                try:
                    d = Decimal(v1) - Decimal(min0)
                    end = Decimal(d) / Decimal(_range)
                    h1 = float(end)
                except InvalidOp:
                    h1 = 0.0

                datatype = type(v)

                if datatype not in _subclasses_by_type:
                    Subclass = type(datatype.__name__.title(), (datatype,), {})
                    _subclasses_by_type[datatype] = Subclass

                Subclass = _subclasses_by_type[datatype]

                replacement = Subclass(v)
                replacement.histo = (h0 * 100, h1 * 100)
                r[k] = replacement
