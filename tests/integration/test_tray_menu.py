import sys
from difflib import SequenceMatcher

import pytest
from PySide6 import QtGui

from normcap.gui.tray import screengrab

from .testcases import testcases


@pytest.mark.gui()
def test_tray_menu_exit(monkeypatch, qtbot, run_normcap):
    """Test if application can be exited through tray icon."""
    # GIVEN NormCap is started to tray via "background-mode"
    tray = run_normcap(extra_cli_args=["--background-mode"])

    exit_calls = []
    monkeypatch.setattr(sys, "exit", lambda code: exit_calls.append(code))

    # WHEN "exit" is clicked in system tray menu
    tray.tray_menu.show()
    exit_action = tray.tray_menu.findChild(QtGui.QAction, "exit")
    exit_action.trigger()

    # THEN the NormCap should exit with exit code 0
    qtbot.waitUntil(lambda: len(exit_calls) > 0)
    assert exit_calls == [0]


@pytest.mark.gui()
def test_tray_menu_capture(monkeypatch, qtbot, run_normcap, select_region):
    """Test if capture mode can be started through tray icon."""
    # GIVEN NormCap is started to tray via "background-mode"
    #       and with a certain test image as screenshot
    tray = run_normcap(
        extra_cli_args=["--language=eng", "--mode=parse", "--background-mode"]
    )
    assert not tray.windows

    testcase = testcases[0]
    monkeypatch.setattr(
        screengrab, "get_capture_func", lambda: lambda: [testcase.image_scaled]
    )

    exit_calls = []
    monkeypatch.setattr(sys, "exit", lambda code: exit_calls.append(code))

    # WHEN "capture" is clicked in system tray menu
    #      and a region on the screen is selected
    tray.tray_menu.show()

    capture_action = tray.tray_menu.findChild(QtGui.QAction, "capture")
    capture_action.trigger()

    select_region(on=tray.windows[0], pos=testcase.coords_scaled)

    # THEN text should be captured
    #      and close to the ground truth
    #      and normcap should _not_ exit
    qtbot.waitUntil(lambda: tray.capture.ocr_text is not None)

    capture = tray.capture
    assert capture

    similarity = SequenceMatcher(
        None, capture.ocr_text, testcase.ocr_transformed
    ).ratio()
    assert similarity >= 0.98, f"{capture.ocr_text=}"

    assert not exit_calls

    # Cleanup
    tray._exit_application(delayed=False)
    tray.deleteLater()