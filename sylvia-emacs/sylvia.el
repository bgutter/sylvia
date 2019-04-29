;;; sylvia.el --- Poetry and lyrics major-mode for emacs               -*- lexical-binding: t; -*-

;; Copyright (C) 2019  Brandon Guttersohn

;; Author: Brandon Guttersohn <code@guttersohn.org>
;; Keywords: poetry poem lyrics phonetics sylvia rhyme syllable
;; Version: 0.0.1

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <http://www.gnu.org/licenses/>.

;;; Commentary:

;; !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
;; !!! This is a generated file! See sylvia.org for full documentation. !!!
;; !!! and to make any changes.                                         !!!
;; !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

;;; Code:

(require 'epc)
(require 'dash)

(defvar sylvia:epc-manager nil "EPC Manager Object for Sylvia.")
(make-variable-buffer-local 'sylvia:epc-manager)

(defun sylvia:start-epc ()
  "Start the EPC server & create the client."
  (interactive)
  (if sylvia:epc-manager
    (sylvia:stop-epc))
  (setq sylvia:epc-manager (epc:start-epc "python2" '("-m" "sylvia" "-e"))))

(defun sylvia:stop-epc ()
  "Stop the EPC server and release the client."
  (epc:stop-epc sylvia:epc-manager)
  (setq sylvia:epc-manager nil))

(defun sylvia:--epc-sync (func args)
  "Call a Sylvia command synchronously."
  (epc:call-sync sylvia:epc-manager func args))

(defun sylvia:--epc-async (func args cb)
  "Call a Sylvia command asynchronously with a callback."
  (deferred:$
    ;(deferred:wait-idle 1000)
    (epc:call-deferred sylvia:epc-manager func args)
    (deferred:nextc it cb)))

(defun sylvia:--epc-sync-or-async (func args cb)
  "Call a Sylvia command async if callback given, else synchronously."
  (if cb
      (sylvia:--epc-async func args cb)
    (sylvia:--epc-sync func args)))

(defun sylvia:lookup (word &optional callback)
  "Lookup the phonemes for a word. If callback is given, the call is async."
  (sylvia:--epc-sync-or-async 'lookup `(,word) callback))

(defun sylvia:infer (word &optional callback)
  "Infer the phonemes for a word. If callback is given, the call is async."
  (sylvia:--epc-sync-or-async 'infer `(,word) callback))

(defun sylvia:rhyme (word &optional rhyme-level callback)
  "Find rhymes for a word. If callback is given, the call is async."
  (sylvia:--epc-sync-or-async 'rhyme `(,word ,(symbol-name rhyme-level)) callback))

(defun sylvia:update-poem (&optional buffer-name callback)
  "Update Sylvia instance with buffer contents. If callback is given, the call is async."
  (let*
      ((buffer-name (or buffer-name (buffer-name)))
       (content     (with-current-buffer (get-buffer buffer-name) (buffer-substring-no-properties (point-min) (point-max)))))
    (sylvia:--epc-sync-or-async 'update_poem `(,content) callback)))

(defun sylvia:poem-syllable-counts (&optional callback)
  "Get syllable counts for current poem. If callback is given, the call is async."
  (sylvia:--epc-sync-or-async 'poem_syllable_counts `() callback))

(defvar sylvia-mode-hook nil
  "Hooks to be run when sylvia-mode is invoked.")

(defvar sylvia-mode-map
  (let ((map (make-keymap)))
    (define-key map (kbd "C-c C-r") 'sylvia:copy-rhyme-at-point-as-kill)
    map)
  "Keymap for sylvia-mode.")

(defvar sylvia-mode-syntax-table
  (let ((st (make-syntax-table)))
    (modify-syntax-entry ?' "w" st) ;; apostrophes are part of words
    st)
  "Syntax table for sylvia-mode")

(defface sylvia:syllable-count-margin-face '((t :foreground "#FFFF00"))
  "Face used to decorate syllable counts in window margin."
  :group 'sylvia)

(defvar sylvia:idle-timer nil)
(defvar sylvia:idle-delay 0.5)
(make-variable-buffer-local 'sylvia:idle-timer)

(defun sylvia-mode ()
  "Major mode for editing text with a focus on phonetic values."
  (interactive)

  ;; clean up buffer variables
  (kill-all-local-variables)

  ;; Start the EPC server & run Sylvia
  (sylvia:start-epc)

  ;; 'officially' change the major mode
  (setq major-mode 'sylvia-mode)
  (setq mode-name "Sylvia")

  ;; apply syntax table, keymaps
  (set-syntax-table sylvia-mode-syntax-table)
  (use-local-map sylvia-mode-map)

  ;; start the idle timer, attach post-command hooks
  (setq sylvia:idle-timer (run-with-idle-timer sylvia:idle-delay t 'sylvia:idle-actions))
  (add-hook 'post-command-hook 'sylvia:post-command-actions nil t)

  ;; run any mode-hooks
  (run-hooks 'sylvia-mode-hook))

(defun sylvia:mode-p ()
  "Sylvia the current major mode?"
  (eq major-mode 'sylvia-mode))

(defun sylvia:idle-actions ()
  "Test")

(defun sylvia:post-command-actions ()
    "Run after every command."
    (when (sylvia:mode-p)
      (sylvia:apply-buffer-changes)
      (sylvia:echo-phonemes-at-point)
      (sylvia:update-syllable-margins)))

(defun sylvia:apply-buffer-changes ()
    (interactive)
    "Update contents of buffer into Sylvia."
    (sylvia:update-poem (buffer-name)  (lambda (x))))

(defun sylvia:echo-phonemes-at-point ()
  "Display phonetic representation of word at point in the echo area."
  (when (null (current-message))
    (let*
        ((word          (thing-at-point 'word 'no-properties)))
      (when word
        (sylvia:lookup word (sylvia:--echo-phonemes-at-point--deferred-generator word))))))

(defun sylvia:--echo-phonemes-at-point--deferred-generator (word)
  "Deferred callback generator for `sylvia:echo-phonemes-at-point'"
  (lexical-let
      ((captured-word word))
    #'(lambda (phoneme-reprs)
        (when phoneme-reprs
          (let ((message-log-max nil))
            (message "%s: %s" captured-word phoneme-reprs))))))

(defvar sylvia:syllable-count-overlays nil)

(defun sylvia:update-syllable-margins ()
  "Update left margin to show syllable counts."
  (sylvia:poem-syllable-counts #'sylvia:--update-syllable-margins--deferred))

(defun sylvia:--update-syllable-margins--deferred (sylcounts)
  (interactive)
  "Update left margin to show syllable counts."
  ;; ensure this is buffer-local (don't think I'm doing this right?)
  (make-local-variable 'sylvia:syllable-count-overlays)
  ;; clear previous overlays
  (dolist (ov sylvia:syllable-count-overlays)
    (delete-overlay ov))
  ;; add new overlays
  (save-excursion
    (let*
        ((win (get-buffer-window (current-buffer)))
         (sylcounts (-slice sylcounts (- (line-number-at-pos (window-start win)) 1))))
      (goto-char (window-start win))
      (while (not (eobp))
        (let*
            ((ov     (make-overlay (point) (point)))
             (cnt    (format "% 4s" (number-to-string (first sylcounts))))
             (cntstr (if (> (string-to-number cnt) 0) cnt "    ")))
          (put-text-property 0 (length cntstr) 'font-lock-face 'sylvia:syllable-count-margin-face cntstr)
          (push ov sylvia:syllable-count-overlays)
          (overlay-put ov 'before-string (propertize " " 'display `((margin left-margin) ,cntstr)))
          (setq sylcounts (cdr sylcounts)))
      (forward-line))
    (set-window-margins win 4))))

(defun my-presorted-completion-table (completions)
  "Bypass completing-read's desire to sort items we send. Modified with lexical let from here:
https://emacs.stackexchange.com/questions/8115/make-completing-read-respect-sorting-order-of-a-collection
NOTE: Works for built-in and helm, but ivy still sorts."
  (lexical-let ((captured-completions completions))
    (lambda (string pred action)
      (if (eq action 'metadata)
          `(metadata (display-sort-function . ,#'identity))
        (complete-with-action action captured-completions string pred)))))

(defun sylvia:copy-rhyme-at-point-as-kill (prefix-arg)
  "Interactively list rhymes for thing at point, placing selected word into kill-ring.
Without prefix arg, use Sylvia's default rhyme-level.
With C-u prefix, use Sylvia's 'loose' rhyme-level.
With C-u C-u prefix args, use Sylvia's 'perfect' rhyme-level."
  (interactive "P")
  (let*
      ((ivy-sort-functions-alist nil) ;; workaround ivy always sorting entries
       (word                     (thing-at-point 'word 'no-properties))
       (rhyme-level              (cond ((equal prefix-arg '(4))  'loose)
                                       ((equal prefix-arg '(16)) 'perfect)
                                       (t                        'default)))
       (rhyme                    (and word (completing-read
                                   (format "[%s] Rhymes for %s: " (symbol-name rhyme-level) word)
                                   (my-presorted-completion-table (sylvia:rhyme word rhyme-level))))))
    (if rhyme
        (progn
          (kill-new (downcase rhyme))
          (message "Pushed %S onto the kill-ring." rhyme))
      (message "Nothing at point!"))))

(provide 'sylvia)
;;; sylvia.el ends here
