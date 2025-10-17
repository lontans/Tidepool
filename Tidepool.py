from textual.app import App, ComposeResult
from textual.widgets import Input, Static, Label, Checkbox, Header, Button, Footer, ProgressBar, TabbedContent, TabPane, TextArea, Select
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.color import Gradient
from textual import on
from textual.message import Message
from textual.containers import Container
from textual_plotext import PlotextPlot
from textual.reactive import reactive
from textual.message import Message
import textwrap
import asyncio
import json
import os
import random

#/Users/jonathansong/Desktop/Tidepool

class Headline(Static):

    def compose(self) -> None:
        yield Label("Tidepool", id = "title_header")
        yield Label("", id="daily_title")
    
    def on_mount(self) -> None:
        self.New_Quote()
    
    def New_Quote(self) -> None:
        with open("quotes.json", "r") as file:
            file_data = json.load(file)
            quote_number = random.randint(1,11)
            quote_text = file_data[f"Quote {quote_number}"]["quote_text"]
            quote_source = file_data[f"Quote {quote_number}"]["source"]
            quote_content = (f"\n {quote_text} - {quote_source}\n")
            self.query_one("#daily_title").update(f"{quote_content}")

class Tide_Hub(Static):
    CSS_PATH = "style.tcss"
    
    def compose(self) -> ComposeResult:
        with TabbedContent(initial = "stats", id = "tabs"):
            yield Stats_Hub("Stats", id = "stats")
            yield Hubs("Hubs", id = "hubs")
            yield Todays_Tide("Journal", id = "journal")
            yield Entry_History("Previous entries", id = "previousEntries")

class DailySubmitPressed(Message):
    pass

class Hubs(TabPane):
    def compose(self) -> ComposeResult:
       with TabbedContent(initial = "fitnessHub"):
            yield Fitness("Fitness 💪", id = "fitnessHub")
            yield Creative("Creative 🎨", id = "creativeHub")
            yield Academics("Uni Prep🎓", id = "academicsHub")
            yield Chess("Chess ♟️", id = "chessHub")
            yield Misc("Misc 🤷", id = "miscHub")
            yield TestHub("Test", id = "testHub")


class Fitness(TabPane):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            FitnessTodolist(id = "fitnessTodolist"),
            FitnessStats(id = "fitnessStats"),
        )
class FitnessTodolist(Static):
    tasks_completed = 1
    task_number = 1
    todo_dict = {f"Task {task_number}":{
        "todo_text":None,
        "completed_status":None,
        "removed_status": None
    }}

    def on_mount(self) -> None:
        if os.stat("fitness.json").st_size==0:
            return
        else:
            with open("fitness.json", "r") as file:
                data = json.load(file)
                self.task_number = len(data)+1
                todo_number = 1
                for key in data:
                    task_text = data[key]["todo_text"]
                    if data[key]["completed_status"] == False and data[key]["removed_status"] == False:
                        new_task = Horizontal(
                            Checkbox(f"{task_text}", id = f"fitness_task_{todo_number}", classes = "todolist_tasks"),
                            Button("-", variant = "error", id = f"fitness_task_remove_{todo_number}", classes = "remove_buttons"),
                            id = f"fitness_task_{todo_number}_container", classes = "task_containers")
                        self.query_one("#fitness_task_container").mount(new_task)
                        todo_number+=1
                    else:
                        self.query_one("#fitness_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {task_text}"))
                        self.tasks_completed+=1
                        todo_number+=1
                self.todo_dict.clear()
                new_data = {f"Task {self.task_number}":{
                    "todo_text":None,
                    "completed_status":None,
                    "removed_status": None,
                }}
                self.todo_dict.update(new_data)

    def compose(self) -> ComposeResult:
       todo_tab_widgets = Vertical(
        Horizontal(
            Input(placeholder = "Add task...", id = "fitness_input_task"),
            Button("+", variant = "success", id = "fitness_task_add"),
            id = "fitness_todolist_bar"
        ),
        VerticalScroll(id = "fitness_task_container", classes = "task_container"),
       )
       completed_tab_widgets  = VerticalScroll(
        Label("Completed Tasks:"), id = "fitness_completed_task_container"
       )

       with TabbedContent(initial = "fitnessTodoTab"):
            yield TabPane("Todo", todo_tab_widgets, id = "fitnessTodoTab")
            yield TabPane("Completed", completed_tab_widgets, id = "fitnessCompletedTab")
    
    def Todolist_Save(self) -> None:
        if os.stat("fitness.json").st_size == 0:
            with open("fitness.json", "w") as file:
                data = self.todo_dict
                json.dump(data, file, indent=4)
        else:
            with open("fitness.json", "r") as file:
                data=json.load(file)
                data.update(self.todo_dict)
            with open ("fitness.json", "w") as file:
                json.dump(data, file, indent=4)
        #Update Previous Entries
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "fitness_task_add":
            self.AddTask()
        if str(event.button.id).startswith("fitness_task_remove") == True:
            eventID = event.button.id
            self.DeleteTask(eventID)

    def AddTask(self) -> None:
        task_text = self.query_one("#fitness_input_task", Input).value
        Current_Task = f"Task {self.task_number}"
        self.todo_dict[Current_Task]["todo_text"] = task_text
        self.todo_dict[Current_Task]["completed_status"] = False
        self.todo_dict[Current_Task]["removed_status"] = False
    
        if not task_text.strip():
            return

        new_task = Horizontal(
            Checkbox(f"{task_text}", id = f"fitness_task_{self.task_number}", classes = "todolist_tasks"),
            Button("-", variant = "error", id = f"fitness_task_remove_{self.task_number}", classes = "remove_buttons"),
            id = f"fitness_task_{self.task_number}_container", classes = "task_containers")

        self.Todolist_Save()
        self.query_one("#fitness_task_container").mount(new_task)
        self.query_one("#fitness_input_task").value = ""

        self.todo_dict.clear()
        self.task_number += 1
        new_data = {f"Task {self.task_number}":{
            "todo_text":None,
            "completed_status":None,
            "removed_status":None
        }}
        self.todo_dict.update(new_data)
    
    def DeleteTask(self, eventID) -> None:
        deleteable_task_num = "".join(filter(str.isdigit, eventID))
        deleteable_task = self.query_one(f"#fitness_task_{deleteable_task_num}_container")
        deleteable_task.remove()
        with open("fitness.json", "r") as file:
            data = json.load(file)
            data[f"Task {deleteable_task_num}"]["removed_status"] = True
        with open("fitness.json", "w") as file:
            json.dump(data, file, indent=4)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        finished_task = self.query_one(f"#{event.checkbox.id}")
        finished_task_num = "".join(filter(str.isdigit, event.checkbox.id))
        finished_task_container = self.query_one(f"#fitness_task_{finished_task_num}_container")

        with open("fitness.json", "r") as file:
            data = json.load(file)
            data[f"Task {finished_task_num}"]["completed_status"] = True
            if os.stat("fitness.json").st_size != 0:
                with open("fitness.json", "w") as file:
                    json.dump(data, file, indent=4)

        self.query_one("#fitness_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {finished_task.label}"))
        finished_task_container.remove() #remove old task from the todolist dom
        self.tasks_completed += 1

class FitnessStats(Static):
    run_distance = []
    date = []

    def on_mount(self) -> None:
        rplt = self.query_one("#runDistanceGraph", PlotextPlot).plt
        rplt.plot(self.date, self.run_distance, color = "green", marker = "hd")
        rplt.title("Running Hawaii")
        rplt.xlabel("Day")
        rplt.ylabel("Distance")
        if os.stat("data.json").st_size != 0:
            self.Load_Saved_Data()
        return

    def compose(self) -> ComposeResult:
        run_stats_widgets = Vertical(
            PlotextPlot(id="runDistanceGraph"),
            ProgressBar(total = 428, show_eta = True, id = "hawaii_bar"),
            )
        yield run_stats_widgets

    def on_daily_submit_pressed(self, message: DailySubmitPressed) -> None:
        self.Append_Plot()

    def Append_Plot(self):
        with open("data.json", mode = "r", encoding = "utf-8") as file:        
            file_data = json.load(file)
            day_number = len(file_data)
            Current_Run_Distance = int(file_data[f"Day {day_number}"]["run"])
            Total_Run_Distance = self.run_distance[-1] + Current_Run_Distance
            self.run_distance.append(Total_Run_Distance)

            self.date.append(len(self.run_distance))
            self.Replot()

    def Load_Saved_Data(self) -> None:
        #updating plotext textual plot
        with open("data.json", mode = "r", encoding = "utf-8") as file:        
            file_data = json.load(file)
            for day in file_data:
                #test without the int method later
                Current_Run_Distance = file_data[day]["run"]
                if self.run_distance == []:
                    self.run_distance.append(Current_Run_Distance)
                elif self.run_distance != []:
                    self.run_distance.append(int(self.run_distance[-1]+Current_Run_Distance))

                self.date.append(len(self.run_distance))
            self.Replot()

    def Replot(self) -> None:
        rgraph = self.query_one("#runDistanceGraph", PlotextPlot).plt
        rgraph.clear_data()
        rgraph.plot(self.date, self.run_distance, color = "green", marker = "hd")
        self.query_one("#runDistanceGraph", PlotextPlot).refresh(repaint = True)



class Creative(TabPane):
    tasks_completed = 1
    task_number = 1
    todo_dict = {f"Task {task_number}":{
        "todo_text":None,
        "completed_status":None,
        "removed_status": None
    }}

    def on_mount(self) -> None:
        if os.stat("creative.json").st_size==0:
            return
        else:
            with open("creative.json", "r") as file:
                data = json.load(file)
                self.task_number = len(data)+1
                todo_number = 1
                for key in data:
                    task_text = data[key]["todo_text"]
                    if data[key]["completed_status"] == False and data[key]["removed_status"] == False:
                        new_task = Horizontal(
                            Checkbox(f"{task_text}", id = f"creative{todo_number}", classes = "todolist_tasks"),
                            Button("-", variant = "error", id = f"creative_task_remove_{todo_number}", classes = "remove_buttons"),
                            id = f"creative_task_{todo_number}_container", classes = "task_containers")
                        self.query_one("#creative_task_container").mount(new_task)
                        todo_number+=1
                    else:
                        self.query_one("#creative_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {task_text}"))
                        self.tasks_completed+=1
                        todo_number+=1
                self.todo_dict.clear()
                new_data = {f"Task {self.task_number}":{
                    "todo_text":None,
                    "completed_status":None,
                    "removed_status": None,
                }}
                self.todo_dict.update(new_data)

    def compose(self) -> ComposeResult:
       todo_tab_widgets = Vertical(
        Horizontal(
            Input(placeholder = "Add task...", id = "creative_input_task"),
            Button("+", variant = "success", id = "creative_task_add"),
            id = "creative_todolist_bar"
        ),
        VerticalScroll(id = "creative_task_container", classes = "task_container"),
       )
       completed_tab_widgets  = VerticalScroll(
        Label("Completed Tasks:"), id = "creative_completed_task_container"
       )

       with TabbedContent(initial = "creativeTodoTab"):
            yield TabPane("Todo", todo_tab_widgets, id = "creativeTodoTab")
            yield TabPane("Completed", completed_tab_widgets, id = "creativeCompletedTab")
    
    def Todolist_Save(self) -> None:
        if os.stat("creative.json").st_size == 0:
            with open("creative.json", "w") as file:
                data = self.todo_dict
                json.dump(data, file, indent=4)
        else:
            with open("creative.json", "r") as file:
                data=json.load(file)
                data.update(self.todo_dict)
            with open ("creative.json", "w") as file:
                json.dump(data, file, indent=4)
        #Update Previous Entries
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "creative_task_add":
            self.AddTask()
        if str(event.button.id).startswith("creative_task_remove") == True:
            eventID = event.button.id
            self.DeleteTask(eventID)

    def AddTask(self) -> None:
        task_text = self.query_one("#creative_input_task", Input).value
        Current_Task = f"Task {self.task_number}"
        self.todo_dict[Current_Task]["todo_text"] = task_text
        self.todo_dict[Current_Task]["completed_status"] = False
        self.todo_dict[Current_Task]["removed_status"] = False
    
        if not task_text.strip():
            return

        new_task = Horizontal(
            Checkbox(f"{task_text}", id = f"creative_task_{self.task_number}", classes = "todolist_tasks"),
            Button("-", variant = "error", id = f"creative_task_remove_{self.task_number}", classes = "remove_buttons"),
            id = f"creative_task_{self.task_number}_container", classes = "task_containers")

        self.Todolist_Save()
        self.query_one("#creative_task_container").mount(new_task)
        self.query_one("#creative_input_task").value = ""

        self.todo_dict.clear()
        self.task_number += 1
        new_data = {f"Task {self.task_number}":{
            "todo_text":None,
            "completed_status":None,
            "removed_status":None
        }}
        self.todo_dict.update(new_data)
    
    def DeleteTask(self, eventID) -> None:
        deleteable_task_num = "".join(filter(str.isdigit, eventID))
        deleteable_task = self.query_one(f"#creative_task_{deleteable_task_num}_container")
        deleteable_task.remove()
        with open("creative.json", "r") as file:
            data = json.load(file)
            data[f"Task {deleteable_task_num}"]["removed_status"] = True
        with open("creative.json", "w") as file:
            json.dump(data, file, indent=4)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        finished_task = self.query_one(f"#{event.checkbox.id}")
        finished_task_num = "".join(filter(str.isdigit, event.checkbox.id))
        finished_task_container = self.query_one(f"#creative_task_{finished_task_num}_container")

        with open("creative.json", "r") as file:
            data = json.load(file)
            data[f"Task {finished_task_num}"]["completed_status"] = True
            if os.stat("creative.json").st_size != 0:
                with open("creative.json", "w") as file:
                    json.dump(data, file, indent=4)

        self.query_one("#creative_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {finished_task.label}"))
        finished_task_container.remove() #remove old task from the todolist dom
        self.tasks_completed += 1


class Academics(TabPane):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            AcademicsTodolist(id = "academicsTodolist"),
            AcademicsStats(id = "academicsStats"),
        )
class AcademicsTodolist(Static):
    tasks_completed = 1
    task_number = 1
    todo_dict = {f"Task {task_number}":{
        "todo_text":None,
        "completed_status":None,
        "removed_status": None
    }}

    def on_mount(self) -> None:
        if os.stat("academics.json").st_size==0:
            return
        else:
            with open("academics.json", "r") as file:
                data = json.load(file)
                self.task_number = len(data)+1
                todo_number = 1
                for key in data:
                    task_text = data[key]["todo_text"]
                    if data[key]["completed_status"] == False and data[key]["removed_status"] == False:
                        new_task = Horizontal(
                            Checkbox(f"{task_text}", id = f"academics{todo_number}", classes = "todolist_tasks"),
                            Button("-", variant = "error", id = f"academics_task_remove_{todo_number}", classes = "remove_buttons"),
                            id = f"academics_task_{todo_number}_container", classes = "task_containers")
                        self.query_one("#academics_task_container").mount(new_task)
                        todo_number+=1
                    else:
                        self.query_one("#academics_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {task_text}"))
                        self.tasks_completed+=1
                        todo_number+=1
                self.todo_dict.clear()
                new_data = {f"Task {self.task_number}":{
                    "todo_text":None,
                    "completed_status":None,
                    "removed_status": None,
                }}
                self.todo_dict.update(new_data)

    def compose(self) -> ComposeResult:
       todo_tab_widgets = Vertical(
        Horizontal(
            Input(placeholder = "Add task...", id = "academics_input_task"),
            Button("+", variant = "success", id = "academics_task_add"),
            id = "academics_todolist_bar"
        ),
        VerticalScroll(id = "academics_task_container", classes = "task_container"),
       )
       completed_tab_widgets  = VerticalScroll(
        Label("Completed Tasks:"), id = "academics_completed_task_container"
       )

       with TabbedContent(initial = "academicsTodoTab"):
            yield TabPane("Todo", todo_tab_widgets, id = "academicsTodoTab")
            yield TabPane("Completed", completed_tab_widgets, id = "academicsCompletedTab")
    
    def Todolist_Save(self) -> None:
        if os.stat("academics.json").st_size == 0:
            with open("academics.json", "w") as file:
                data = self.todo_dict
                json.dump(data, file, indent=4)
        else:
            with open("academics.json", "r") as file:
                data=json.load(file)
                data.update(self.todo_dict)
            with open ("academics.json", "w") as file:
                json.dump(data, file, indent=4)
        #Update Previous Entries
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "academics_task_add":
            self.AddTask()
        if str(event.button.id).startswith("academics_task_remove") == True:
            eventID = event.button.id
            self.DeleteTask(eventID)

    def AddTask(self) -> None:
        task_text = self.query_one("#academics_input_task", Input).value
        Current_Task = f"Task {self.task_number}"
        self.todo_dict[Current_Task]["todo_text"] = task_text
        self.todo_dict[Current_Task]["completed_status"] = False
        self.todo_dict[Current_Task]["removed_status"] = False
    
        if not task_text.strip():
            return

        new_task = Horizontal(
            Checkbox(f"{task_text}", id = f"academics_task_{self.task_number}", classes = "todolist_tasks"),
            Button("-", variant = "error", id = f"academics_task_remove_{self.task_number}", classes = "remove_buttons"),
            id = f"academics_task_{self.task_number}_container", classes = "task_containers")

        self.Todolist_Save()
        self.query_one("#academics_task_container").mount(new_task)
        self.query_one("#academics_input_task").value = ""

        self.todo_dict.clear()
        self.task_number += 1
        new_data = {f"Task {self.task_number}":{
            "todo_text":None,
            "completed_status":None,
            "removed_status":None
        }}
        self.todo_dict.update(new_data)
    
    def DeleteTask(self, eventID) -> None:
        deleteable_task_num = "".join(filter(str.isdigit, eventID))
        deleteable_task = self.query_one(f"#academics_task_{deleteable_task_num}_container")
        deleteable_task.remove()
        with open("academics.json", "r") as file:
            data = json.load(file)
            data[f"Task {deleteable_task_num}"]["removed_status"] = True
        with open("academics.json", "w") as file:
            json.dump(data, file, indent=4)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        finished_task = self.query_one(f"#{event.checkbox.id}")
        finished_task_num = "".join(filter(str.isdigit, event.checkbox.id))
        finished_task_container = self.query_one(f"#academics_task_{finished_task_num}_container")

        with open("academics.json", "r") as file:
            data = json.load(file)
            data[f"Task {finished_task_num}"]["completed_status"] = True
            if os.stat("academics.json").st_size != 0:
                with open("academics.json", "w") as file:
                    json.dump(data, file, indent=4)

        self.query_one("#academics_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {finished_task.label}"))
        finished_task_container.remove() #remove old task from the todolist dom
        self.tasks_completed += 1

class AcademicsStats(Static):
    study_duration = []
    date = []

    def on_mount(self) -> None:
        splt = self.query_one("#studyDurationGraph", PlotextPlot).plt
        splt.plot(self.date, self.study_duration, color = "green", marker = "hd")
        splt.title("Time Spent Studying")
        splt.xlabel("Day")
        splt.ylabel("Duration")
        if os.stat("data.json").st_size != 0:
            self.Load_Saved_Data()
        return

    def compose(self) -> ComposeResult:
        run_stats_widgets = PlotextPlot(id="studyDurationGraph")
        yield run_stats_widgets

    def on_daily_submit_pressed(self, message: DailySubmitPressed) -> None:
        self.Append_Plot()

    def Append_Plot(self):
        with open("data.json", mode = "r", encoding = "utf-8") as file:        
            file_data = json.load(file)
            day_number = len(file_data)
            Current_Study_Duration = int(file_data[f"Day {day_number}"]["academics"])
            Total_Study_Duration = self.study_duration[-1] + Current_Study_Duration
            self.study_duration.append(Total_Study_Duration)

            self.date.append(len(self.study_duration))
            self.Replot()

    def Load_Saved_Data(self) -> None:
        #updating plotext textual plot
        with open("data.json", mode = "r", encoding = "utf-8") as file:        
            file_data = json.load(file)
            for day in file_data:
                #test without the int method later
                Current_Study_Duration = file_data[day]["academics"]
                if self.study_duration == []:
                    self.study_duration.append(Current_Study_Duration)
                elif self.study_duration != []:
                    self.study_duration.append(int(self.study_duration[-1]+Current_Study_Duration))

                self.date.append(len(self.study_duration))
            self.Replot()

    def Replot(self) -> None:
        sgraph = self.query_one("#studyDurationGraph", PlotextPlot).plt
        sgraph.clear_data()
        sgraph.plot(self.date, self.study_duration, color = "green", marker = "hd")
        self.query_one("#studyDurationGraph", PlotextPlot).refresh(repaint = True)



class Chess(TabPane):   
    def compose(self) -> ComposeResult:
        yield Horizontal(
            ChessTodolist(id = "chessTodolist"),
            ChessStats(id = "chessStats"),
        )

class ChessTodolist(Static):
    tasks_completed = 1
    task_number = 1
    todo_dict = {f"Task {task_number}":{
        "todo_text":None,
        "completed_status":None,
        "removed_status": None
    }}
    def on_mount(self) -> None:
        if os.stat("chess.json").st_size != 0:
            with open("chess.json", "r") as file:
                data = json.load(file)
                self.task_number = len(data)+1
                todo_number = 1
                for key in data:
                    task_text = data[key]["todo_text"]
                    if data[key]["completed_status"] == False and data[key]["removed_status"] == False:
                        new_task = Horizontal(
                            Checkbox(f"{task_text}", id = f"chess{todo_number}", classes = "todolist_tasks"),
                            Button("-", variant = "error", id = f"chess_task_remove_{todo_number}", classes = "remove_buttons"),
                            id = f"chess_task_{todo_number}_container", classes = "task_containers")
                        self.query_one("#chess_task_container").mount(new_task)
                        todo_number+=1
                    else:
                        self.query_one("#chess_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {task_text}"))
                        self.tasks_completed+=1
                        todo_number+=1
                self.todo_dict.clear()
                new_data = {f"Task {self.task_number}":{
                    "todo_text":None,
                    "completed_status":None,
                    "removed_status": None,
                }}
                self.todo_dict.update(new_data)
            return

    def compose(self) -> ComposeResult:
        todo_tab_widgets = Vertical(
            Horizontal(
                Input(placeholder="Add task...", id="chess_input_task"),
                Button("+", variant="success", id="chess_task_add"),
                id="chess_todolist_bar"
            ),
            VerticalScroll(id="chess_task_container", classes="task_container"),
        )

        completed_tab_widgets = VerticalScroll(
            Label("Completed Tasks:"), id="chess_completed_task_container"
        )

        with TabbedContent(initial="chessTodoTab", id="chessTodoTabs"):
            yield TabPane("Todo", todo_tab_widgets, id="chessTodoTab")
            yield TabPane("Completed", completed_tab_widgets, id="chessCompletedTab")

    def Todolist_Save(self) -> None:
        if os.stat("chess.json").st_size == 0:
            with open("chess.json", "w") as file:
                data = self.todo_dict
                json.dump(data, file, indent=4)
        else:
            with open("chess.json", "r") as file:
                data=json.load(file)
                data.update(self.todo_dict)
            with open ("chess.json", "w") as file:
                json.dump(data, file, indent=4)
        #Update Previous Entries
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "chess_task_add":
            self.AddTask()
        if str(event.button.id).startswith("chess_task_remove") == True:
            eventID = event.button.id
            self.DeleteTask(eventID)

    def AddTask(self) -> None:
        task_text = self.query_one("#chess_input_task", Input).value
        Current_Task = f"Task {self.task_number}"
        self.todo_dict[Current_Task]["todo_text"] = task_text
        self.todo_dict[Current_Task]["completed_status"] = False
        self.todo_dict[Current_Task]["removed_status"] = False
    
        if not task_text.strip():
            return

        new_task = Horizontal(
            Checkbox(f"{task_text}", id = f"chess_task_{self.task_number}", classes = "todolist_tasks"),
            Button("-", variant = "error", id = f"chess_task_remove_{self.task_number}", classes = "remove_buttons"),
            id = f"chess_task_{self.task_number}_container", classes = "task_containers")

        self.Todolist_Save()
        self.query_one("#chess_task_container").mount(new_task)
        self.query_one("#chess_input_task").value = ""

        self.todo_dict.clear()
        self.task_number += 1
        new_data = {f"Task {self.task_number}":{
            "todo_text":None,
            "completed_status":None,
            "removed_status":None
        }}
        self.todo_dict.update(new_data)
    
    def DeleteTask(self, eventID) -> None:
        deleteable_task_num = "".join(filter(str.isdigit, eventID))
        deleteable_task = self.query_one(f"#chess_task_{deleteable_task_num}_container")
        deleteable_task.remove()
        with open("chess.json", "r") as file:
            data = json.load(file)
            data[f"Task {deleteable_task_num}"]["removed_status"] = True
        with open("chess.json", "w") as file:
            json.dump(data, file, indent=4)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        finished_task = self.query_one(f"#{event.checkbox.id}")
        finished_task_num = "".join(filter(str.isdigit, event.checkbox.id))
        finished_task_container = self.query_one(f"#chess_task_{finished_task_num}_container")

        with open("chess.json", "r") as file:
            data = json.load(file)
            data[f"Task {finished_task_num}"]["completed_status"] = True
            if os.stat("chess.json").st_size != 0:
                with open("chess.json", "w") as file:
                    json.dump(data, file, indent=4)

        self.query_one("#chess_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {finished_task.label}"))
        finished_task_container.remove() #remove old task from the todolist dom
        self.tasks_completed += 1

class ChessStats(Static):
    chess_elo = []
    date = []

    def on_mount(self) -> None:
        cplt = self.query_one("#chessEloGraph", PlotextPlot).plt
        cplt.plot(self.date, self.chess_elo, color = "green", marker = "hd")
        cplt.title("Chess Elo Journey")
        cplt.xlabel("Day")
        cplt.ylabel("Elo")
        cplt.ylim(800,1100)
        if os.stat("data.json").st_size != 0:
            self.Load_Saved_Data()
        return

    def compose(self) -> ComposeResult:
        chess_stats_widgets = PlotextPlot(id="chessEloGraph")
        yield chess_stats_widgets

    def on_daily_submit_pressed(self, message: DailySubmitPressed) -> None:
        self.Append_Plot()

    def Append_Plot(self):
        with open("data.json", mode = "r", encoding = "utf-8") as file:        
            file_data = json.load(file)
            day_number = len(file_data)
            Current_Chess_Elo = file_data[f"Day {day_number}"]["chess"]
            self.chess_elo.append(Current_Chess_Elo)
            self.date.append(len(self.chess_elo))
            self.Replot()

    def Load_Saved_Data(self) -> None:
        #updating plotext textual plot
        with open("data.json", mode = "r", encoding = "utf-8") as file:        
            file_data = json.load(file)
            for day in file_data:
                #test without the int method later
                Current_Chess_Elo = file_data[day]["chess"]
                self.chess_elo.append(Current_Chess_Elo)
                self.date.append(len(self.chess_elo))
            self.Replot()

    def Replot(self) -> None:
        cgraph = self.query_one("#chessEloGraph", PlotextPlot).plt
        cgraph.clear_data()
        cgraph.plot(self.date, self.chess_elo, color = "green", marker = "hd")
        cgraph.ylim(800,1100)
        self.query_one("#chessEloGraph", PlotextPlot).refresh(repaint = True)


class Misc(TabPane):
    tasks_completed = 1
    task_number = 1
    todo_dict = {f"Task {task_number}":{
        "todo_text":None,
        "completed_status":None,
        "removed_status": None
    }}

    def on_mount(self) -> None:
        if os.stat("misc.json").st_size==0:
            return
        else:
            with open("misc.json", "r") as file:
                data = json.load(file)
                self.task_number = len(data)+1
                todo_number = 1
                for key in data:
                    task_text = data[key]["todo_text"]
                    if data[key]["completed_status"] == False and data[key]["removed_status"] == False:
                        new_task = Horizontal(
                            Checkbox(f"{task_text}", id = f"misc{todo_number}", classes = "todolist_tasks"),
                            Button("-", variant = "error", id = f"misc_task_remove_{todo_number}", classes = "remove_buttons"),
                            id = f"misc_task_{todo_number}_container", classes = "task_containers")
                        self.query_one("#misc_task_container").mount(new_task)
                        todo_number+=1
                    else:
                        self.query_one("#misc_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {task_text}"))
                        self.tasks_completed+=1
                        todo_number+=1
                self.todo_dict.clear()
                new_data = {f"Task {self.task_number}":{
                    "todo_text":None,
                    "completed_status":None,
                    "removed_status": None,
                }}
                self.todo_dict.update(new_data)

    def compose(self) -> ComposeResult:
       todo_tab_widgets = Vertical(
        Horizontal(
            Input(placeholder = "Add task...", id = "misc_input_task"),
            Button("+", variant = "success", id = "misc_task_add"),
            id = "misc_todolist_bar"
        ),
        VerticalScroll(id = "misc_task_container", classes = "task_container"),
       )
       completed_tab_widgets  = VerticalScroll(
        Label("Completed Tasks:"), id = "misc_completed_task_container"
       )

       with TabbedContent(initial = "miscTodoTab"):
            yield TabPane("Todo", todo_tab_widgets, id = "miscTodoTab")
            yield TabPane("Completed", completed_tab_widgets, id = "miscCompletedTab")
    
    def Todolist_Save(self) -> None:
        if os.stat("misc.json").st_size == 0:
            with open("misc.json", "w") as file:
                data = self.todo_dict
                json.dump(data, file, indent=4)
        else:
            with open("misc.json", "r") as file:
                data=json.load(file)
                data.update(self.todo_dict)
            with open ("misc.json", "w") as file:
                json.dump(data, file, indent=4)
        #Update Previous Entries
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "misc_task_add":
            self.AddTask()
        if str(event.button.id).startswith("misc_task_remove") == True:
            eventID = event.button.id
            self.DeleteTask(eventID)

    def AddTask(self) -> None:
        task_text = self.query_one("#misc_input_task", Input).value
        Current_Task = f"Task {self.task_number}"
        self.todo_dict[Current_Task]["todo_text"] = task_text
        self.todo_dict[Current_Task]["completed_status"] = False
        self.todo_dict[Current_Task]["removed_status"] = False
    
        if not task_text.strip():
            return

        new_task = Horizontal(
            Checkbox(f"{task_text}", id = f"misc_task_{self.task_number}", classes = "todolist_tasks"),
            Button("-", variant = "error", id = f"misc_task_remove_{self.task_number}", classes = "remove_buttons"),
            id = f"misc_task_{self.task_number}_container", classes = "task_containers")

        self.Todolist_Save()
        self.query_one("#misc_task_container").mount(new_task)
        self.query_one("#misc_input_task").value = ""

        self.todo_dict.clear()
        self.task_number += 1
        new_data = {f"Task {self.task_number}":{
            "todo_text":None,
            "completed_status":None,
            "removed_status":None
        }}
        self.todo_dict.update(new_data)
    
    def DeleteTask(self, eventID) -> None:
        deleteable_task_num = "".join(filter(str.isdigit, eventID))
        deleteable_task = self.query_one(f"#misc_task_{deleteable_task_num}_container")
        deleteable_task.remove()
        with open("misc.json", "r") as file:
            data = json.load(file)
            data[f"Task {deleteable_task_num}"]["removed_status"] = True
        with open("misc.json", "w") as file:
            json.dump(data, file, indent=4)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        finished_task = self.query_one(f"#{event.checkbox.id}")
        finished_task_num = "".join(filter(str.isdigit, event.checkbox.id))
        finished_task_container = self.query_one(f"#misc_task_{finished_task_num}_container")

        with open("misc.json", "r") as file:
            data = json.load(file)
            data[f"Task {finished_task_num}"]["completed_status"] = True
            if os.stat("misc.json").st_size != 0:
                with open("misc.json", "w") as file:
                    json.dump(data, file, indent=4)

        self.query_one("#misc_completed_task_container").mount(Label(f"\n    {self.tasks_completed}. {finished_task.label}"))
        finished_task_container.remove() #remove old task from the todolist dom
        self.tasks_completed += 1



#test - hubs!
class TestHub(TabPane):
    def compose(self) -> None:
        tasks = TabPane("Tab1"),TabPane("Tab2"),   

        yield Horizontal(
            Content1(id = "test_static1"),
            Content2(id = "test_static2"),) 
class Content1(Static):
    def compose(self) -> None:
        with TabbedContent(initial = "aloo_aloo"):
            yield TabPane("alooo", id = "aloo_aloo")
            yield TabPane("hey there", id = "hey_there")
class Content2(Static):
    def compose(self) -> None:
        yield Label("Gosh it's nice over there")


class Todays_Tide(TabPane):
    Old_Date = 0
    daily_data_dict = {f"Day {Old_Date}":{
        "entry":None,
        "mood":None,
        "duolingo":None,
        "brush":None,
        "sleep":None,
        "chess":None,
        "run":None,
        "academics":None,
    }}

    def on_mount(self) -> None:
        if os.stat("data.json").st_size == 0:
            return
        else:
            with open("data.json", "r") as file:
                data = json.load(file)
                self.Old_Date = len(data)
                new_dictionary = {f"Day {self.Old_Date}":{
                    "entry":None,
                    "mood":None,
                    "duolingo":None,
                    "brush":None,
                    "sleep":None,
                    "chess":None,
                    "run":None,
                    "academics":None,
                }}
                self.daily_data_dict.clear()
                self.daily_data_dict.update(new_dictionary)
    

    def compose(self) -> ComposeResult:
        art_text = """            ___   ____
          /' --;^/ ,-_\      \ | /
         / / --o\ o-\ \ \   --(_)--
        /-/-/|o|-|\-\ \| \   / | \ 
         '`  ` |-|   `` '
               |-|
               |-|
               |-|
            ...|-|..........
        ,;;;;;;;;;;;;;;;;;;;;;;;;,.
    ~~,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,~~~~
    ~;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,  ______   """
        yield Horizontal(
            Label(f"{art_text}", id = "dailyTideArt"),
            Checkbox("Duolingo", id = "duolingo_check", classes = "small_daily_checks"),
            Checkbox("Brushed Teeth", id = "brush_check", classes = "small_daily_checks"),
            Input (placeholder = "Mood/10", id = "mood_in", classes = "small_daily_checks"),
            Input(placeholder = "Hours Slept", id = "sleep_in", classes = "small_daily_checks"),
            Input(placeholder = "Chess Elo", id = "chessIn", classes = "small_daily_checks"),
            Input(placeholder = "Run Distance", id = "runIn", classes = "small_daily_checks"),
            Input(placeholder = "Study Time", id = "academicsIn", classes = "small_daily_checks"),
            Button("Submit!", variant = "success", id = "daily_submit", classes = "small_daily_checks"),             
            id = "daily_result")
        yield Vertical(
            Label(" Diary:", id = "diaryHeader"),
            TextArea("", id = "diary_in"),
            id = "diary_container"
        )
    
    def External_Save(self) -> None:
        #JSON Portion
        if os.stat("data.json").st_size == 0:
            with open("data.json", "w") as file:
                data = self.daily_data_dict
                json.dump(data, file, indent=4)
        else:
            with open("data.json", "r") as file:
                data=json.load(file)
                data.update(self.daily_data_dict)
            with open ("data.json", "w") as file:
                json.dump(data, file, indent=4)
        #Update Previous Entries

    @on(Button.Pressed, "#daily_submit")
    async def save_entry(self) -> None:
        Diary_Entry = self.query_one("#diary_in", TextArea).text
        Mood_Level = int(self.query_one("#mood_in", Input).value)
        Sleep_Level = int(self.query_one("#sleep_in", Input).value)
        Chess_Level = int(self.query_one("#chessIn", Input).value)
        Run_Level = int(self.query_one("#runIn", Input).value)
        Academics_Level = int(self.query_one("#academicsIn", Input).value)
        Duolingo_Check = self.query_one("#duolingo_check").value
        Brush_Check = self.query_one("#brush_check").value

        Current_Date = f"Day {self.Old_Date + 1}"
        self.daily_data_dict[f"{Current_Date}"] = self.daily_data_dict.pop(f"Day {self.Old_Date}")
        self.daily_data_dict[f"{Current_Date}"]["entry"] = Diary_Entry
        self.daily_data_dict[f"{Current_Date}"]["mood"] = Mood_Level
        self.daily_data_dict[f"{Current_Date}"]["sleep"] = Sleep_Level
        self.daily_data_dict[f"{Current_Date}"]["chess"] = Chess_Level
        self.daily_data_dict[f"{Current_Date}"]["run"] = Run_Level
        self.daily_data_dict[f"{Current_Date}"]["academics"] = Academics_Level
        self.daily_data_dict[f"{Current_Date}"]["duolingo"] = Duolingo_Check
        self.daily_data_dict[f"{Current_Date}"]["brush"] = Brush_Check

        stats = self.app.query_one("#stats")
        entry_history = self.app.query_one("#previousEntries")
        chessStats = self.app.query_one("#chessStats")
        fitnessStats = self.app.query_one("#fitnessStats")
        academicsStats = self.app.query_one("#academicsStats")
        

        stats.post_message(DailySubmitPressed())
        entry_history.post_message(DailySubmitPressed())
        chessStats.post_message(DailySubmitPressed())
        fitnessStats.post_message(DailySubmitPressed())
        academicsStats.post_message(DailySubmitPressed())
        

        self.External_Save()

        self.query_one("#duolingo_check").value = False
        self.query_one("#brush_check").value = False
        self.query_one("#mood_in").value = ""
        self.query_one("#sleep_in").value = ""
        self.query_one("#chessIn").value = ""
        self.query_one("#runIn").value = ""
        self.query_one("#academicsIn").value = ""
        self.query_one("#diary_in").text = ""
        self.Old_Date += 1       

class Stats_Hub(TabPane):     
    mood_level_y =[]
    sleep_level_y = []
    date =[]

    def on_mount(self) -> None:
        mplt = self.query_one("#mood_chart", PlotextPlot).plt
        mplt.plot(self.date, self.mood_level_y, color = "green", marker = "hd")
        mplt.title("Mood Level")
        mplt.xlabel("Day")
        mplt.ylabel("Mood")
        mplt.ylim(0,10)

        splt = self.query_one("#sleepChart", PlotextPlot).plt
        splt.plot(self.date, self.sleep_level_y, color = "green", marker = "hd")
        splt.title("Hours Slept")
        splt.xlabel("Day")
        splt.ylabel("Sleep")
        splt.ylim(0,12)
        if os.stat("data.json").st_size == 0:
            return
        else:
            self.Load_Saved_Data()
    
    def on_daily_submit_pressed(self, message: DailySubmitPressed) -> None:
        self.Append_Plot()
        self.Progress_Update()

    def compose(self) -> ComposeResult:
        Welcome_Text = """
        ▖  ▖  ▜            ▗     ▄▖▘ ▌        ▜ ▌
        ▌▞▖▌█▌▐ ▛▘▛▌▛▛▌█▌  ▜▘▛▌  ▐ ▌▛▌█▌▛▌▛▌▛▌▐ ▌
        ▛ ▝▌▙▖▐▖▙▖▙▌▌▌▌▙▖  ▐▖▙▌  ▐ ▌▙▌▙▖▙▌▙▌▙▌▐▖▖
                                        ▌        
        """

        gradient = Gradient.from_colors(
            "#439FFA",
            "#57C785",
            "#BBFF69",
        ) 
        yield Horizontal(
                Vertical(
                    PlotextPlot(id = "mood_chart"),
                    PlotextPlot(id = "sleepChart"),
                ),
                Vertical(
                    Vertical(
                        Label("Horizon Stats", id = "horizon_label"),
                        Label(),
                        Horizontal(
                            Label("Duolingo % "),
                            ProgressBar(total = 100, show_eta = False, id = "duolingo_bar", gradient = gradient),
                        ),
                        Horizontal(
                            Label("Teethbrush % "),
                            ProgressBar(total = 100, show_eta = False, id = "teethbrush_bar", gradient = gradient),
                        ),
                        Horizontal(
                            Label("Vibes % "),
                            ProgressBar(total = 10, show_eta = False, id = "vibes_bar", gradient = gradient),
                        ),
                        id = "progress_bars"),
                    Label(f"{Welcome_Text}"),
                ),
            id = "todays_data_display")
    
    def Load_Saved_Data(self) -> None:
        #updating plotext textual plot
        with open("data.json", mode = "r", encoding = "utf-8") as file:        
            file_data = json.load(file)
            for day in file_data:
                #test without the int method later
                Current_Mood = file_data[day]["mood"]
                Current_Sleep = file_data[day]["sleep"]
                self.mood_level_y.append(Current_Mood)
                self.sleep_level_y.append(Current_Sleep)
                self.date.append(len(self.mood_level_y))
            self.Replot()
        #updating progress bars
        self.Progress_Update()
        

    def Progress_Update(self) -> None:
        with open("data.json", mode = "r", encoding = "utf-8")  as file:
            file_data = json.load(file)
            day_number = len(file_data)
            duolingo_number = 0
            brush_number = 0
            for day in file_data:
                if file_data[day]["duolingo"] == True:
                    duolingo_number += 1
                if file_data[day]["brush"] == True:
                    brush_number += 1
            duolingo_percent = (duolingo_number/day_number)*100
            brush_percent = (brush_number/day_number)*100
            vibes_percent = (sum(self.mood_level_y)/day_number)
            #self.query_one("#test").update(content = f"{sum(self.mood_level_y), {day_number}, {duolingo_number}, {brush_number}}")

            self.query_one("#duolingo_bar", ProgressBar).update(progress=duolingo_percent)
            self.query_one("#teethbrush_bar", ProgressBar).update(progress=brush_percent)
            self.query_one("#vibes_bar", ProgressBar).update(progress=vibes_percent)
    
    def Append_Plot(self):
        with open("data.json", mode = "r", encoding = "utf-8") as file:        
            file_data = json.load(file)
            day_number = len(file_data)
            Current_Mood = file_data[f"Day {day_number}"]["mood"]
            Current_Sleep = file_data[f"Day {day_number}"]["sleep"]
            self.mood_level_y.append(Current_Mood)
            self.sleep_level_y.append(Current_Sleep)
            self.date.append(len(self.mood_level_y))
            self.Replot()

    def Replot(self) -> None:
        mgraph = self.query_one("#mood_chart", PlotextPlot).plt
        mgraph.clear_data()
        mgraph.plot(self.date, self.mood_level_y, color = "green", marker = "hd")
        mgraph.ylim(0,10)
        self.query_one("#mood_chart", PlotextPlot).refresh(repaint = True)

        sgraph = self.query_one("#sleepChart", PlotextPlot).plt
        sgraph.clear_data()
        sgraph.plot(self.date, self.sleep_level_y, color = "green", marker = "hd")
        sgraph.ylim(0,12)
        self.query_one("#sleepChart", PlotextPlot).refresh(repaint = True)

class Entry_History(TabPane):

    def compose(self) -> ComposeResult:
        with TabPane("Previous Entries", id = "previousEntries"):
                with TabbedContent(initial = "week1tab", id = "previous_entries_tabs"):
                    yield TabPane("Week 1", VerticalScroll(id = "week_1"), id = "week1tab")
    
    async def on_mount(self) -> None:
        header = self.query_one("#--content-tab-week1tab")
        header.add_class("entry-tab-button")
        if os.stat("data.json").st_size == 0:
            return
        else:
            await self.Load_Saved_Entries()
    
    async def Load_Saved_Entries(self) -> None:
        with open("data.json", "r") as file:
            file_data = json.load(file)
            day_number = 1
            week_number = int((day_number - 1) / 7)+1
            for entry in file_data:
                await self.Update_Single_Entry(file_data, day_number, week_number)
                day_number += 1
                week_number = int((day_number-1)/7)+1

    async def on_daily_submit_pressed(self, message: DailySubmitPressed) -> None:
        with open("data.json", "r") as file:
            file_data = json.load(file)
            day_number = len(file_data)
            week_number = int((day_number - 1) / 7)+1
            await self.Update_Single_Entry(file_data, day_number, week_number)

    async def Update_Single_Entry(self, file_data, day_number, week_number) -> None:
        entry_text = file_data[f"Day {day_number}"]["entry"]
        mood_check = file_data[f"Day {day_number}"]["mood"]
        sleep_check = file_data[f"Day {day_number}"]["sleep"]
        duolingo_check = file_data[f"Day {day_number}"]["duolingo"]
        brush_check = file_data[f"Day {day_number}"]["brush"]
        chess_check = file_data[f"Day {day_number}"]["chess"]
        run_check = file_data[f"Day {day_number}"]["run"]
        study_check = file_data[f"Day {day_number}"]["academics"]

        if duolingo_check == True:
            duolingo_text = "✅"
        elif duolingo_check == False:
            duolingo_text = "❌"

        if brush_check == True:
            brush_text = "✅"
        elif brush_check == False:
            brush_text = "❌"

        header_line = f"Day {day_number}:       Mood: {mood_check}   Sleep: {sleep_check}   Chess Elo: {chess_check}   Distance Run: {run_check}   Time Studying: {study_check}   Duolingo {duolingo_text}   Brushed Teeth {brush_text}"
        wrapped_text = textwrap.fill(entry_text.strip(), width = 100)
        daily_entry = f"\n{header_line}\n\n{wrapped_text}"

        if (day_number - 1) % 7 == 0 and day_number != 1:
            new_pane = TabPane(f"Week {week_number}", VerticalScroll(id = f"week_{week_number}"), id = f"week{week_number}tab")
            await self.query_one("#previous_entries_tabs").add_pane(new_pane)
            header = self.query_one(f"#--content-tab-week{week_number}tab")
            header.add_class("entry-tab-button")
            self.query_one(f"#week_{week_number}").mount(Label(daily_entry))
        else:
            self.query_one(f"#week_{week_number}").mount(Label(daily_entry))       


class Tidepool(App):
    CSS_PATH = "style.tcss"  
    def compose(self) -> ComposeResult:
            yield Headline()
            yield Tide_Hub()
            yield Footer()
 
if __name__ == "__main__": 
    app = Tidepool()
    app.run()

    #ideas:
    #distance ran per week using the textual stats widget
    #current chess elo/chess books I want to read
    #habit streaks per month?
    #random fact of stats home page?