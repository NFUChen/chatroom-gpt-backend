import subprocess
import threading
import uuid
import time


class CommandExecutor:
    def __init__(self) -> None:
        self.process = None
        self.should_kill = False
        self.is_executing = True
        self.MAX_QUEUE_SIZE = 500
        self.logs_queue = []
        self.current_id = str(uuid.uuid4())
        self.retrive_id = str(uuid.uuid4())

    def _enque_log(self, log: str) -> None:
        self.current_id = str(uuid.uuid4())
        self.logs_queue.append(log)

    def _is_full_log_queue(self) -> bool:
        return len(self.logs_queue) == self.MAX_QUEUE_SIZE
    
    
    def _init_popen(self, command: str) -> None:
        try: 
            self.clear_log_queue()
            self.is_executing  = True
            self.process = subprocess.Popen(
                command.split(" "), 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                universal_newlines=True,
            )
            self._flush_output()
            time.sleep(0.1)
            self.is_executing = False
        except Exception as error:
            print(error)
    
    def execute(self, command: str) -> None:
        if self.process is not None:
            self.process.kill()

        threading.Thread(target=lambda: self._init_popen(command)).start()
        
    def _flush_output(self) -> None:
        for line in self.process.stdout:
            self._handle_kill_process()
            self._handle_log_queue(line)
        err = "\n".join([line for line in self.process.stderr])
        print(err, flush= True)
        self._handle_kill_process()

    def get_log(self) -> list[str]:
        '''
        Only getting log if there is a change in current_id
        '''
        if self.retrive_id == self.current_id:
            return []
        self.retrive_id = self.current_id
        return self.logs_queue

    def kill_current_process(self) -> None:
        self.should_kill = True


    def _handle_log_queue(self, log: str) -> None:

        if self._is_full_log_queue():
            self.logs_queue.pop(0)
        self._enque_log(log.replace("\n", ""))

    def clear_log_queue(self) -> None:
        self.logs_queue = []
        
    def _handle_kill_process(self) -> None:

        if self.should_kill:
            self.process.terminate()
            self.should_kill = False
            self.clear_log_queue()
            return