from server.models import Observation, Action, Reward
from tasks import easy_task, medium_task, hard_task
from graders import grade


class MedicalTriageEnv:

    def __init__(self):
        self._task_index = 0  
        self.patient = None
        self.steps = 0
        self.done = False

    def reset(self):
        task_cycle = ["easy", "medium", "hard"]
        current_task = task_cycle[self._task_index % 3]

        if current_task == "easy":
            self.patient = easy_task()
        elif current_task == "medium":
            self.patient = medium_task()
        else:
            self.patient = hard_task()


        self._task_index += 1

        self.steps = 0
        self.done = False

        return Observation(
            symptoms=self.patient["symptoms"],
            pain_level=self.patient["pain_level"],
            age=self.patient["age"],
            step=self.steps,
        )

    def step(self, action: Action):
        self.steps += 1

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
            ),
            score,
            done,
            {},
        )

    def state(self):
        return self.patient