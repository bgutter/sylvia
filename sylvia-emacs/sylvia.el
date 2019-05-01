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

(defun sylvia:regex (phoneme-regex &optional callback)
  "Search for words whose pronunciation matches the given phoneme-regex.
Assume a typical Python regular expression, with the following additions:

  * # matches any consonant phoneme
  * @ matches any vowel phoneme
  * % matches any syllable (equivalent to #*@#*)
  * Whitespace is irrelevant and will be removed, but must be used to separate
    consecutive phoneme literals.
  * See cmudict documentation for list of phoneme literals.
  * Full sequence matching is done by default. That is, we automatically add '^'
    to the start of the regex, and '$' at the end. Prepend or append '.*' to your
    regex to override this behavior.

Try it out:
  regex S IH #*V#* % AH

If callback is given, the call is async."
  (sylvia:--epc-sync-or-async 'regex `(,phoneme-regex) callback))

(defun sylvia:update-poem (&optional buffer-name callback)
  "Update Sylvia instance with buffer contents. If callback is given, the call is async."
  (let*
      ((buffer-name (or buffer-name (buffer-name)))
       (content     (with-current-buffer (get-buffer buffer-name) (buffer-substring-no-properties (point-min) (point-max)))))
    (sylvia:--epc-sync-or-async 'update_poem `(,content) callback)))

(defun sylvia:poem-syllable-counts (&optional callback)
  "Get syllable counts for current poem. If callback is given, the call is async."
  (sylvia:--epc-sync-or-async 'poem_syllable_counts `() callback))

(defun sylvia:poem-phonemes-in-region (begin end &optional callback)
  "Get phonemes in the associated region."
  (sylvia:--epc-sync-or-async 'poem_phonemes_in_region `(,begin ,end) callback))

(defvar sylvia-mode-hook nil
  "Hooks to be run when sylvia-mode is invoked.")

(defvar sylvia-mode-map
  (let ((map (make-keymap)))
    (define-key map (kbd "C-c C-r") 'sylvia:copy-rhyme-at-point-as-kill)
    (define-key map (kbd "C-c C-q") 'sylvia:copy-regex-query-result-as-kill)
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

(defface sylvia:vowel-face '((t :foreground "HotPink1"))
  "Face used to decorate vowel phonemes."
  :group 'sylvia)

(defface sylvia:consonant-face '((t :foreground "cornflower blue"))
  "Face used to decorate consonant."
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
      (sylvia:update-echo)
      (sylvia:update-syllable-margins)))

(defun sylvia:apply-buffer-changes ()
    (interactive)
    "Update contents of buffer into Sylvia."
    (sylvia:update-poem (buffer-name)  (lambda (x))))

(defun sylvia:update-echo ()
  "If region is active, display their phonemes in the echo area. Else,
show phonemes for the word at point."
  (when (null (current-message))
    (if (use-region-p)
        (sylvia:--echo-phonemes-in-region)
      (sylvia:--echo-phonemes-at-point))))

(defun sylvia:--echo-phonemes-in-region ()
  "Display phonetic representation of the selected region in the echo area."
  (sylvia:poem-phonemes-in-region
    (1- (region-beginning)) ;; emacs buffers are 1-indexed
    (1- (region-end))       ;; sylvia is 0-indexed
    (sylvia:--echo-phonemes--deferred-generator
      (buffer-substring-no-properties (region-beginning) (region-end)))))

(defun sylvia:--echo-phonemes-at-point ()
  "Display phonetic representation of word at point in the echo area."
  (let*
      ((bounds (bounds-of-thing-at-point 'word))
       (begin  (and bounds (car bounds)))
       (end    (and bounds (cdr bounds))))
    (when (and begin end)
      (sylvia:poem-phonemes-in-region
        (1- begin)
        (1- end)
        (sylvia:--echo-phonemes--deferred-generator
          (buffer-substring-no-properties begin end))))))

(defun sylvia:--echo-phonemes--deferred-generator (text)
  "Deferred callback generator for `sylvia:echo-phonemes-in-region' and `sylvia:echo-phonemes-at-point'"
  (lexical-let
      ((captured-text text))
    #'(lambda (phoneme-reprs)
        (when phoneme-reprs
          (let*
              ((fontified-phoneme-reprs (mapcar #'sylvia:--fontify-phonemes--echo phoneme-reprs))
               (phoneme-str             (string-join fontified-phoneme-reprs " ")))
          (sylvia:--message-no-log "%s: %s" captured-text phoneme-str))))))

(defun sylvia:--fontify-phonemes--echo (phoneme)
  "Apply face to phoneme prior for use in echo area."
  (if (sylvia:--phoneme-vowel-p phoneme)
      (propertize phoneme 'face 'sylvia:vowel-face)
    (propertize phoneme 'face 'sylvia:consonant-face)))

(defvar sylvia:syllable-count-overlays nil)
(make-variable-buffer-local 'sylvia:syllable-count-overlays)

(defun sylvia:update-syllable-margins ()
  "Update left margin to show syllable counts."
  (sylvia:poem-syllable-counts #'sylvia:--update-syllable-margins--deferred))

(defun sylvia:--update-syllable-margins--deferred (sylcounts)
  (interactive)
  "Update left margin to show syllable counts."
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
    (sylvia:--loudly-try-push-kill-ring rhyme)))

(defun sylvia:copy-regex-query-result-as-kill ()
  "Interactively search for words using a phonetic regex.
See documentation for `sylvia:regex' for full details."
  (interactive)
  (let*
      ((ivy-sort-functions-alist nil) ;; workaround ivy always sorting entries
       (initial       (if (use-region-p) (sylvia:--region-phonemes) ""))
       (phoneme-regex (read-string "Enter Phoneme Regex: " (string-join initial " ")))
       (result        (completing-read
                        (format "Words matching pattern %s: " phoneme-regex)
                        (my-presorted-completion-table (sylvia:regex phoneme-regex)))))
    (sylvia:--loudly-try-push-kill-ring result)))

;; TODO

(defun my-presorted-completion-table (completions)
  "Bypass completing-read's desire to sort items we send. Modified with lexical let from here:
https://emacs.stackexchange.com/questions/8115/make-completing-read-respect-sorting-order-of-a-collection
NOTE: Works for built-in and helm, but ivy still sorts."
  (lexical-let ((captured-completions completions))
    (lambda (string pred action)
      (if (eq action 'metadata)
          `(metadata (display-sort-function . ,#'identity))
        (complete-with-action action captured-completions string pred)))))

(defun sylvia:--loudly-try-push-kill-ring (entry)
  "If entry is non-nil, place it into the kill-ring and announce it. Else, complain."
  (if entry
      (progn
        (kill-new (downcase entry))
        (message "Pushed %S onto the kill-ring." entry))
    (message "Nothing at point!")))

(defun sylvia:--message-no-log (&rest args)
  "Write a message to the echo area, but keep it out of the messages buffer."
  (let ((message-log-max nil))
     (apply 'message args)))

(defun sylvia:--region-phonemes ()
  "Return a list of the phonemes covered by words in region. If a word has multiple possible pronunciations,
choose the 'best' one. Returns a list of strings."
  (sylvia:poem-phonemes-in-region (1- (region-beginning)) (1- (region-end))))

(defun sylvia:--phoneme-vowel-p (phoneme)
  "Is this a vowel phoneme?"
  (member phoneme (mapcar #'symbol-name '(AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW))))

(provide 'sylvia)
;;; sylvia.el ends here
