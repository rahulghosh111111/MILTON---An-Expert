"""Captures the current screen as the brain's schema expects: active app,
a flattened list of interactive elements, and OCR'd visible text.

Windows-only (uiautomation + pywin32). Degrades to an empty-but-valid
screen_context on any failure so the main loop never crashes on this step.
"""


def _bounding_to_pos(rect):
    return {
        "x": rect.left,
        "y": rect.top,
        "w": rect.right - rect.left,
        "h": rect.bottom - rect.top,
    }


def _walk(control, elements, max_depth, depth, max_elements):
    if depth > max_depth or len(elements) >= max_elements:
        return

    for child in control.GetChildren():
        try:
            el_type = (child.ControlTypeName or "text").lower()
            label = child.Name or ""
            try:
                text_content = child.GetValuePattern().Value
            except Exception:
                text_content = label

            rect = child.BoundingRectangle
            if rect.width() > 0 and rect.height() > 0:
                elements.append(
                    {
                        "id": f"{el_type}_{len(elements)}",
                        "type": el_type,
                        "label": label,
                        "text_content": text_content,
                        "position": _bounding_to_pos(rect),
                        "focused": bool(child.HasKeyboardFocus),
                    }
                )
        except Exception:
            pass

        if len(elements) >= max_elements:
            return
        _walk(child, elements, max_depth, depth + 1, max_elements)


def _ocr_window(hwnd):
    try:
        import pytesseract
        import win32gui
        from PIL import ImageGrab

        rect = win32gui.GetWindowRect(hwnd)
        img = ImageGrab.grab(bbox=rect)
        return pytesseract.image_to_string(img).strip()
    except Exception:
        return ""


def get_screen_context(max_depth=4, max_elements=200):
    try:
        import uiautomation as auto
        import win32gui

        hwnd = win32gui.GetForegroundWindow()
        active_app = win32gui.GetWindowText(hwnd) or "Unknown"
        root = auto.ControlFromHandle(hwnd)

        elements = []
        _walk(root, elements, max_depth, depth=0, max_elements=max_elements)
    except Exception as exc:
        return {
            "active_app": "Unknown",
            "elements": [],
            "visible_text": "",
            "_error": str(exc),
        }

    return {
        "active_app": active_app,
        "elements": elements,
        "visible_text": _ocr_window(hwnd),
    }
