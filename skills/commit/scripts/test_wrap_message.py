#!/usr/bin/env python3
"""Regression tests for wrap_message.py."""

from __future__ import annotations

import contextlib
import io
import subprocess
import unittest
from unittest.mock import patch

import wrap_message


def response(returncode: int, status: int | None) -> subprocess.CompletedProcess[str]:
    stdout = f"HTTP/2.0 {status} Status\n" if status is not None else ""
    return subprocess.CompletedProcess([], returncode, stdout, "")


class ApiStatusTests(unittest.TestCase):
    def test_accepts_successful_2xx_response(self) -> None:
        with patch.object(
            wrap_message.subprocess, "run", return_value=response(0, 200)
        ):
            self.assertEqual(wrap_message.api_status("repos/fork/repo"), (200, None))

    def test_preserves_http_failure_status(self) -> None:
        with patch.object(
            wrap_message.subprocess, "run", return_value=response(1, 403)
        ):
            self.assertEqual(
                wrap_message.api_status("repos/fork/repo"), (403, "HTTP 403")
            )

    def test_reports_missing_gh_without_exposing_os_error(self) -> None:
        with patch.object(
            wrap_message.subprocess, "run", side_effect=OSError("secret")
        ):
            self.assertEqual(
                wrap_message.api_status("repos/fork/repo"),
                (None, "gh is unavailable"),
            )


class ReferenceResolutionTests(unittest.TestCase):
    def test_rewrites_only_after_repository_success_and_issue_404(self) -> None:
        references = wrap_message.References("fork/repo", "upstream/repo")
        with patch.object(
            wrap_message,
            "api_status",
            side_effect=[(200, None), (404, "HTTP 404")],
        ) as probe:
            self.assertEqual(references.target("123"), "upstream/repo")
            self.assertEqual(references.target("123"), "upstream/repo")

        self.assertEqual(
            probe.call_args_list,
            [
                unittest.mock.call("repos/fork/repo"),
                unittest.mock.call("repos/fork/repo/issues/123"),
            ],
        )

    def test_inaccessible_repository_leaves_all_references_unknown(self) -> None:
        references = wrap_message.References("missing/repo", "upstream/repo")
        stderr = io.StringIO()
        with (
            patch.object(
                wrap_message, "api_status", return_value=(404, "HTTP 404")
            ) as probe,
            contextlib.redirect_stderr(stderr),
        ):
            self.assertIsNone(references.target("123"))
            self.assertIsNone(references.target("456"))

        probe.assert_called_once_with("repos/missing/repo")
        self.assertEqual(
            stderr.getvalue(),
            "could not access missing/repo (HTTP 404); "
            "leaving bare references unchanged\n",
        )

    def test_non_404_issue_failure_leaves_reference_unknown(self) -> None:
        references = wrap_message.References("fork/repo", "upstream/repo")
        stderr = io.StringIO()
        with (
            patch.object(
                wrap_message,
                "api_status",
                side_effect=[(200, None), (403, "HTTP 403")],
            ),
            contextlib.redirect_stderr(stderr),
        ):
            self.assertIsNone(references.target("123"))

        self.assertEqual(
            stderr.getvalue(),
            "could not resolve #123 in fork/repo (HTTP 403); leaving it unchanged\n",
        )


class TrackingReferences(wrap_message.References):
    def __init__(self) -> None:
        super().__init__("fork/repo", "upstream/repo")
        self.lookups: list[str] = []

    def target(self, number: str) -> str | None:
        self.lookups.append(number)
        return self.upstream


class StructuralProtectionTests(unittest.TestCase):
    def test_only_qualifies_safe_prose(self) -> None:
        references = TrackingReferences()
        message = """subject #1

Ordinary prose refers to #2 and is long enough to wrap normally.

````markdown
```sh
echo #3
```
~~~text
#4
~~~
````

Fixes: #5

BREAKING CHANGE: preserve #6

- keep #7

    echo #8

Run `echo #9` and keep this inline shell comment exactly as written.

This-paragraph-has-a-word-that-is-far-too-long-for-the-width #10
"""

        wrapped = wrap_message.wrap_message(
            message.rstrip("\n"), 40, 20, True, references
        )

        self.assertEqual(wrapped.splitlines()[0], "subject #1")
        self.assertIn("upstream/repo#2", wrapped)
        for unchanged in (
            "echo #3",
            "#4",
            "Fixes: #5",
            "BREAKING CHANGE: preserve #6",
            "- keep #7",
            "    echo #8",
            "Run `echo #9` and keep this inline",
            "This-paragraph-has-a-word-that-is-far-too-long-for-the-width #10",
        ):
            self.assertIn(unchanged, wrapped)
        self.assertEqual(references.lookups, ["2"])

    def test_inline_code_reflows_without_splitting_or_qualifying(self) -> None:
        references = TrackingReferences()
        message = (
            "subject\n\nCalling `git commit -m #11` on `master` refers to #12 "
            "and `#13`, so this paragraph wraps."
        )
        wrapped = wrap_message.wrap_message(message, 40, 20, True, references)
        self.assertEqual(
            wrapped,
            "subject\n\n"
            "Calling `git commit -m #11` on `master`\n"
            "refers to upstream/repo#12 and `#13`, so\n"
            "this paragraph wraps.",
        )
        self.assertEqual(references.lookups, ["12"])
        self.assertEqual(wrap_message.References.width("`a/b#1` a/b#1"), 11)

    def test_wrap_subject_opt_in_also_qualifies_it(self) -> None:
        references = TrackingReferences()
        wrapped = wrap_message.wrap_message("subject #10", 40, 20, False, references)
        self.assertEqual(wrapped, "subject upstream/repo#10")
        self.assertEqual(references.lookups, ["10"])


if __name__ == "__main__":
    unittest.main()
