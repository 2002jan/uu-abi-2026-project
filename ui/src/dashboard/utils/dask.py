from dask.callbacks import Callback
import time

from dashboard.utils.datetime import format_duration


class PanelProgress(Callback):
    def __init__(self, bar, status=None):
        super().__init__()
        self.bar = bar
        self.status = status
        self._last_pct = -1
        self._start_at = time.time()

    def _start_state(self, dsk, state):
        done = len(state['finished'])
        total = sum(len(state[k]) for k in ("ready", "waiting", "running")) + done
        self.total = max(total, 1)
        self.bar.value = 0
        self._start_at = time.time()

    def _posttask(self, key, result, dsk, state, worker_id):
        pct = int(100 * len(state["finished"]) / self.total)
        if pct != self._last_pct:          # throttle: only push when % changes
            self._last_pct = pct
            self.bar.value = pct

        if self.status is not None:
            now = time.time()
            diff = now - self._start_at


            if pct > 0:
                left = (diff / pct) * (100 - pct)
                dur = format_duration(left)
            else:
                dur = "?"

            self.status.object = f"{pct}% - {dur} estimated left"

    def _finish(self, dsk, state, errored):
        self.bar.value = 100
        if self.status is not None:
            self.status.object = "Failed" if errored else "Done"
