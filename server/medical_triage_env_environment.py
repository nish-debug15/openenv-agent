from server.models import Observation, Action, Reward
from tasks import (
    task_1, task_2, task_3, task_4, task_5, task_6, task_7, task_8,
    task_9, task_10, task_11, task_12, task_13, task_14, task_15
)
from graders import grade


class MedicalTriageEnv:

    def __init__(self):
        self._task_index = 0  
        self.patient = None
        self.steps = 0
        self.done = False
        self.revealed_info = []

    def reset(self):
        tasks_list = [
            task_1, task_2, task_3, task_4, task_5, task_6, task_7, task_8,
            task_9, task_10, task_11, task_12, task_13, task_14, task_15
        ]
        current_task_fn = tasks_list[self._task_index % 15]
        self.patient = current_task_fn()

        self._task_index += 1

        self.steps = 0
        self.done = False
        self.revealed_info = []

        return Observation(
            symptoms=self.patient["symptoms"],
            pain_level=self.patient["pain_level"],
            age=self.patient["age"],
            step=self.steps,
            hidden_info=self.revealed_info.copy()
        )

    def step(self, action: Action):
        self.steps += 1

        if action.action_type == "request_more_info":
            # Reveal one piece of hidden info if available
            hidden = self.patient.get("hidden_info", [])
            if len(self.revealed_info) < len(hidden):
                self.revealed_info.append(hidden[len(self.revealed_info)])
            
            return (
                Observation(
                    symptoms=self.patient["symptoms"],
                    pain_level=self.patient["pain_level"],
                    age=self.patient["age"],
                    step=self.steps,
                    hidden_info=self.revealed_info.copy()
                ),
                0.05,
                False,
                {},
            )
        else:
            predicted = action.content
            true = self.patient["true_severity"]

            score = grade(predicted, true, self.steps)
            done = True

            return (
                Observation(
                    symptoms=self.patient["symptoms"],
                    pain_level=self.patient["pain_level"],
                    age=self.patient["age"],
                    step=self.steps,
                    hidden_info=self.revealed_info.copy()
                ),
                score,
                done,
                {},
            )

    def state(self):
        return self.patient

    def close(self):
        pass