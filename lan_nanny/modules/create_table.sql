CREATE TABLE IF NOT EXISTS scan_log (
        id integer PRIMARY KEY,
        created_ts date,
        end_ts date,
        elapsed_time_sec int,
        completed int,
        success int,
        num_devices int);