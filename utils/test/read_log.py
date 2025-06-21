def load_and_compute_deltas(log_path="sync_log.txt"):
    deltas = []

    with open(log_path, "r") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                cam_ts, frame_name, imu_ts = line.strip().split()
                cam_ts = float(cam_ts)
                frame_name = float(frame_name)
                imu_ts = float(imu_ts)
                delta = cam_ts - imu_ts
                deltas.append(delta)
            except ValueError:
                print(f"[Line {line_number}] Skipping malformed line: {line.strip()}")

    return deltas


if __name__ == "__main__":
    deltas = load_and_compute_deltas("sync_log.txt")

    for i, dt in enumerate(deltas):
        print(f"[{i}] Δt = {dt * 1000:.3f} ms")

    if deltas:
        avg_dt = sum(deltas) / len(deltas)
        max_dt = max(deltas)
        min_dt = min(deltas)
        print("\nSummary:")
        print(f"Total samples : {len(deltas)}")
        print(f"Average Δt     : {avg_dt * 1000:.3f} ms")
        print(f"Min Δt         : {min_dt * 1000:.3f} ms")
        print(f"Max Δt         : {max_dt * 1000:.3f} ms")
    else:
        print("No valid data found.")
