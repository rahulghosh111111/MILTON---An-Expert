"""Executes the brain's "actions" array against the live desktop.

Per the spec: iterate in order, run each step whose requires_confirmation is
false, and halt at the first step where it's true (that step stays pending
for the next turn's yes/no instead of running now).
"""

import time

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def _center(position):
    return (
        position["x"] + position["w"] // 2,
        position["y"] + position["h"] // 2,
    )


def _find_position(target, elements_by_id):
    element_id = (target or {}).get("element_id")
    if element_id and element_id in elements_by_id:
        return elements_by_id[element_id]["position"]
    return None


def _run_one(action, position):
    action_type = action["type"]
    target = action.get("target") or {}
    value = action.get("value")

    if action_type == "open":
        if position:
            pyautogui.click(*_center(position))
        elif value:
            pyautogui.hotkey("win", "r")
            time.sleep(0.3)
            pyautogui.typewrite(value, interval=0.02)
            pyautogui.press("enter")

    elif action_type == "click":
        if position:
            pyautogui.click(*_center(position))

    elif action_type == "write":
        if position:
            pyautogui.click(*_center(position))
        if value:
            pyautogui.typewrite(value, interval=0.02)

    elif action_type == "change":
        if position:
            pyautogui.click(*_center(position))

    elif action_type == "replace":
        if position:
            pyautogui.click(*_center(position))
        pyautogui.hotkey("ctrl", "a")
        if value:
            pyautogui.typewrite(value, interval=0.02)

    elif action_type == "delete":
        if position:
            pyautogui.click(*_center(position))
        pyautogui.press("backspace")

    elif action_type == "remove":
        if position:
            pyautogui.click(*_center(position))
        pyautogui.press("delete")

    elif action_type == "cut":
        if position:
            pyautogui.click(*_center(position))
        pyautogui.hotkey("ctrl", "x")

    elif action_type == "copy":
        if position:
            pyautogui.click(*_center(position))
        pyautogui.hotkey("ctrl", "c")

    elif action_type == "paste":
        if position:
            pyautogui.click(*_center(position))
        pyautogui.hotkey("ctrl", "v")

    elif action_type == "back":
        pyautogui.hotkey("alt", "left")

    elif action_type == "scroll":
        amount = 10 if value == "short" else 30
        description = (target.get("description") or "").lower()
        direction = -1 if "down" in description else 1
        pyautogui.scroll(amount * direction)

    elif action_type == "select":
        if position:
            pyautogui.click(*_center(position))

    elif action_type == "wait":
        time.sleep(float(value) if value else 1.0)

    else:
        raise ValueError(f"unknown action type: {action_type}")


def execute_actions(actions, screen_context):
    elements_by_id = {el["id"]: el for el in screen_context.get("elements", [])}
    executed = []

    for action in actions:
        if action.get("requires_confirmation"):
            break

        position = _find_position(action.get("target"), elements_by_id)
        try:
            _run_one(action, position)
            executed.append({**action, "result": "ok"})
        except Exception as exc:
            executed.append({**action, "result": f"error: {exc}"})
            break

    return executed
