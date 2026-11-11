# Merge Conflict Incident Report & Resolution Note

## 1. Executive Summary
During Sprint 2 development, a deliberate Git merge conflict was engineered between two concurrent feature branches modifying billing concession constants:
- **Branch A (`feature/student-discount-revision`)**: Updated the standard student discount rate from 15% to 18% as part of the annual clinic pricing update.
- **Branch B (`feature/student-discount-promotional`)**: Set the student discount rate to 20% for a seasonal university semester healthcare promotion.

Both branches branched from base commit `21e78b6` and edited the identical line (line 5) in `backend/app/patterns/strategies/discount_strategy.py`.

---

## 2. Technical Reproduction Steps

1. Branch A was created from `main`:
   ```bash
   git checkout -b feature/student-discount-revision
   # Edited STUDENT_DISCOUNT_PERCENTAGE = 0.18
   git commit -m "feat: update baseline student discount rate to 18 percent"
   git push -u origin feature/student-discount-revision
   gh pr create ...
   gh pr merge 10 --merge
   ```
2. Branch B was branched from `21e78b6`:
   ```bash
   git checkout 21e78b6 -b feature/student-discount-promotional
   # Edited STUDENT_DISCOUNT_PERCENTAGE = 0.20
   git commit -m "feat: set student discount promotional rate to 20 percent"
   git push -u origin feature/student-discount-promotional
   gh pr create ...
   ```
3. Attempting to synchronize `origin/main` into `feature/student-discount-promotional`:
   ```bash
   git merge origin/main
   ```
   **Git Result**:
   ```text
   Auto-merging backend/app/patterns/strategies/discount_strategy.py
   CONFLICT (content): Merge conflict in backend/app/patterns/strategies/discount_strategy.py
   Automatic merge failed; fix conflicts and then commit the result.
   ```

---

## 3. The Conflicting Section
The Git conflict diff revealed the simultaneous modifications:

```python
<<<<<<< HEAD
STUDENT_DISCOUNT_PERCENTAGE = 0.20  # Promotional student semester campaign discount 20%
=======
STUDENT_DISCOUNT_PERCENTAGE = 0.18  # Revised standard student concession rate to 18%
>>>>>>> origin/main
```

---

## 4. Conflict Resolution Strategy & Decision

### 4.1 Resolution Decision
The engineering team and clinic billing management agreed to establish **18% as the baseline standard concession rate (`STUDENT_DISCOUNT_PERCENTAGE = 0.18`)** while introducing a configurable promotional discount parameter for seasonal campaigns. This preserves financial stability while supporting promotional marketing.

### 4.2 Resolution Steps Applied
1. Opened `backend/app/patterns/strategies/discount_strategy.py` in the workspace editor.
2. Removed Git boundary markers (`<<<<<<< HEAD`, `=======`, `>>>>>>> origin/main`).
3. Replaced the conflicting block with the reconciled compromise definition:
   ```python
   # Clinic Standard Discount Constants
   STUDENT_DISCOUNT_PERCENTAGE = 0.18  # Baseline student discount (18%) with promotional campaign support
   ```
4. Executed automated pytest suite to verify calculation integrity:
   ```bash
   pytest backend/tests/test_billing.py
   ```
5. Staged the resolved file and the incident documentation:
   ```bash
   git add backend/app/patterns/strategies/discount_strategy.py docs/merge-conflict-note.md
   git commit -m "fix(billing): resolve merge conflict on student discount constant by establishing 18% standard rate"
   git push origin feature/student-discount-promotional
   ```
6. Merged Pull Request #11 into `main` cleanly.
