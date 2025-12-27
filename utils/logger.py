import time
import threading
import functools


def time_logger(label, func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    print(f"⏱️ {label}: {elapsed:.4f} sec")
    return result


def live_stopwatch(func):
    """Decorator untuk menampilkan stopwatch live di terminal saat fungsi dijalankan."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        stop_event = threading.Event()
        start_time = time.time()

        def timer():
            while not stop_event.is_set():
                elapsed = int(time.time() - start_time)
                print(f"\rStopwatch: {elapsed} detik", end="")
                time.sleep(1)

        thread = threading.Thread(target=timer)
        thread.start()

        result = func(*args, **kwargs)  # jalankan fungsi utama

        stop_event.set()  # stop timer
        thread.join()
        elapsed_total = int(time.time() - start_time)
        print(f"\rStopwatch selesai: {elapsed_total} detik")
        return result

    return wrapper
