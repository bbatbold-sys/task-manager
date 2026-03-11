"""Tests for CLI commands using Click's test runner."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import cli


@pytest.fixture
def runner(tmp_path, monkeypatch):
    """CLI runner with isolated storage directory."""
    monkeypatch.chdir(tmp_path)
    return CliRunner()


# --- task add ---

def test_add_basic(runner):
    result = runner.invoke(cli, ["add", "Buy milk"])
    assert result.exit_code == 0
    assert "Added task #1: Buy milk" in result.output


def test_add_with_options(runner):
    result = runner.invoke(cli, [
        "add", "Read book",
        "--description", "Chapter 5",
        "--due", "2026-04-01",
        "--priority", "high",
    ])
    assert result.exit_code == 0
    assert "Added task #1: Read book" in result.output


def test_add_invalid_due_date(runner):
    result = runner.invoke(cli, ["add", "Bad date task", "--due", "not-a-date"])
    assert result.exit_code != 0
    assert "YYYY-MM-DD" in result.output


def test_add_increments_id(runner):
    runner.invoke(cli, ["add", "First"])
    result = runner.invoke(cli, ["add", "Second"])
    assert "Added task #2: Second" in result.output


# --- task list ---

def test_list_empty(runner):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No tasks found" in result.output


def test_list_shows_tasks(runner):
    runner.invoke(cli, ["add", "Alpha"])
    runner.invoke(cli, ["add", "Beta", "--priority", "high"])
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "Alpha" in result.output
    assert "Beta" in result.output


def test_list_filter_status(runner):
    runner.invoke(cli, ["add", "Todo task"])
    runner.invoke(cli, ["add", "Done task"])
    runner.invoke(cli, ["done", "2"])

    result = runner.invoke(cli, ["list", "--status", "done"])
    assert "Done task" in result.output
    assert "Todo task" not in result.output


def test_list_filter_priority(runner):
    runner.invoke(cli, ["add", "High priority", "--priority", "high"])
    runner.invoke(cli, ["add", "Low priority", "--priority", "low"])

    result = runner.invoke(cli, ["list", "--priority", "high"])
    assert "High priority" in result.output
    assert "Low priority" not in result.output


# --- task done ---

def test_done(runner):
    runner.invoke(cli, ["add", "Finish report"])
    result = runner.invoke(cli, ["done", "1"])
    assert result.exit_code == 0
    assert "Task #1 marked as done" in result.output


def test_done_not_found(runner):
    result = runner.invoke(cli, ["done", "99"])
    assert result.exit_code != 0
    assert "not found" in result.output


# --- task delete ---

def test_delete(runner):
    runner.invoke(cli, ["add", "To remove"])
    result = runner.invoke(cli, ["delete", "1"])
    assert result.exit_code == 0
    assert "Task #1 deleted" in result.output

    list_result = runner.invoke(cli, ["list"])
    assert "No tasks found" in list_result.output


def test_delete_not_found(runner):
    result = runner.invoke(cli, ["delete", "99"])
    assert result.exit_code != 0
    assert "not found" in result.output


# --- task search ---

def test_search_finds_match(runner):
    runner.invoke(cli, ["add", "Buy groceries", "--description", "Milk and eggs"])
    result = runner.invoke(cli, ["search", "groceries"])
    assert result.exit_code == 0
    assert "Buy groceries" in result.output


def test_search_no_match(runner):
    runner.invoke(cli, ["add", "Read book"])
    result = runner.invoke(cli, ["search", "python"])
    assert "No tasks matching" in result.output


def test_search_description(runner):
    runner.invoke(cli, ["add", "Random title", "--description", "contains python keyword"])
    result = runner.invoke(cli, ["search", "python"])
    assert "Random title" in result.output
