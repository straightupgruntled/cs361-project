# 🗂️ Dev Project Manager

A lightweight project and task management tool built with **Kivy**, designed to help organize game development work into structured boards with a clean, interactive UI.

---

## Features

### Project Board System

* Create and delete project boards
* Visual project cards with responsive layout
* Delete mode with confirmation prompts

### Task Board System

Each project contains a 3-column kanban-style workflow:

* **Backlog Tasks**
* **Active Tasks**
* **Finished Tasks**

### Task Management

* Add tasks to any column
* Move tasks left/right between columns
* Delete tasks with a confirmation popup
* Edit tasks in a side panel
  * Update name (auto-syncs with UI)
  * Add/edit descriptions

### Task Editing Panel

* Appears on the right side when a task is edited.
* Live updates task data
* Includes:
  * Editable name field
  * Description field
  * Delete button (top-right)
  * Close button (top-left)

### Custom UI Components

All of these custom elements are contained in components/layouts.py

* Colored Box Backgrounds
* Custom Gradient Box Backgrounds
* Rounded Corner Box Containers

---

## Architecture Overview
**TBD**

---

## Getting Started

### Requirements

* Python 3.8 - 3.13 *(3.13 Recommended)*
* Kivy 2.0+

### Install Kivy

```bash
pip install kivy
```

### Run the App

```bash
python main.py
```
