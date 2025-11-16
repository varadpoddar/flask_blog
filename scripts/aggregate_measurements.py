#!/usr/bin/env python3
import sys
import csv
import statistics
from pathlib import Path


def aggregate(csv_file: Path):
    # Support different CSV formats (docker and vagrant). Try to discover
    # a duration column, then collect optional memory and cpu columns.
    durations = []
    cpus = []
    mems_mb = []

    def parse_mem_human(s: str):
        # parse a string like '1.1G/3.8G' or '123M' or '512K' and return used MB
        if not s:
            return None
        # take part before '/' if present
        part = s.split('/')[0].strip()
        try:
            unit = part[-1].upper()
            if unit.isalpha():
                num = float(part[:-1])
                if unit == 'G':
                    return num * 1024
                if unit == 'M':
                    return num
                if unit == 'K':
                    return num / 1024
            else:
                return float(part) / 1024.0  # assume KB -> MB
        except Exception:
            try:
                return float(part)
            except Exception:
                return None

    with csv_file.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            # find duration column
            dur = None
            for k in ('adjusted_duration_seconds', 'original_duration_seconds', 'duration_seconds', 'duration'):
                if k in row and row.get(k):
                    try:
                        dur = float(row.get(k))
                    except Exception:
                        dur = None
                    break

            if dur is not None:
                durations.append(dur)

            # cpu percent: strip percent sign
            cpu_val = None
            if 'cpu_percent' in row and row.get('cpu_percent'):
                s = row.get('cpu_percent').strip().rstrip('%')
                try:
                    cpu_val = float(s)
                    cpus.append(cpu_val)
                except Exception:
                    pass

            # mem_used
            if 'mem_used' in row and row.get('mem_used'):
                m = parse_mem_human(row.get('mem_used'))
                if m is not None:
                    mems_mb.append(m)

    if not durations:
        print('No numeric durations found in', csv_file)
        return 1

    print('File:', csv_file)
    print('Count:', len(durations))
    print('Mean duration (s):', statistics.mean(durations))
    print('Median duration (s):', statistics.median(durations))
    if len(durations) > 1:
        print('Stddev duration (s):', statistics.pstdev(durations))

    if cpus:
        print('\nCPU percent samples:')
        print('Count:', len(cpus))
        print('Mean CPU %:', statistics.mean(cpus))
        print('Median CPU %:', statistics.median(cpus))
    else:
        print('\nNo CPU percent data found in CSV')

    if mems_mb:
        print('\nMemory used samples (MB):')
        print('Count:', len(mems_mb))
        print('Mean used MB:', statistics.mean(mems_mb))
        print('Median used MB:', statistics.median(mems_mb))
    else:
        print('\nNo memory usage data found in CSV')

    return 0


def main():
    if len(sys.argv) < 2:
        print('Usage: aggregate_measurements.py <csv-file>')
        sys.exit(2)
    csv_file = Path(sys.argv[1])
    sys.exit(aggregate(csv_file))


if __name__ == '__main__':
    main()
