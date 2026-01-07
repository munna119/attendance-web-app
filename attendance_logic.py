import pandas as pd
import os
import re
import uuid

def process_attendance(source_file, reference_file, output_dir):

    # STEP 1: READ SOURCE FILE
    df = pd.read_csv(source_file, header=None)
    all_values = df.values.flatten()

    # STEP 2: READ REFERENCE FILE
    ref_df = pd.read_excel(reference_file, header=None)
    ref_rolls = ref_df.iloc[:, 0].astype(str).str.strip().tolist()

    normalized_ref = {
        re.sub(r'[^a-z0-9]', '', r.lower()): r for r in ref_rolls
    }

    # STEP 3: EXTRACT VALID ROLLS
    roll_numbers = []

    for v in all_values:
        val = re.sub(r'[^a-z0-9]', '', str(v).strip().lower())

        if val in normalized_ref:
            roll_numbers.append(normalized_ref[val])
            continue

        if val.isdigit():
            for ref in ref_rolls:
                ref_clean = re.sub(r'[^a-z0-9]', '', ref.lower())
                if ref_clean.endswith(val):
                    roll_numbers.append(ref)
                    break

    roll_numbers = list(dict.fromkeys(roll_numbers))

    # STEP 4: SORT
    def extract_last_digits(s):
        digits = re.findall(r'\d+', s)
        return int(digits[-1]) if digits else 0

    roll_numbers.sort(key=extract_last_digits)

    # STEP 5: SAVE CLEAN ROLL LIST
    clean_df = pd.DataFrame(roll_numbers, columns=["StudentID"])
    clean_file = os.path.join(output_dir, f"clean_{uuid.uuid4().hex}.xlsx")
    clean_df.to_excel(clean_file, index=False)

    # STEP 6: MARK ATTENDANCE
    present_set = {
        re.sub(r'[^a-z0-9]', '', r.lower()) for r in roll_numbers
    }

    attendance = [
        "P" if re.sub(r'[^a-z0-9]', '', r.lower()) in present_set else "A"
        for r in ref_rolls
    ]

    attendance_df = pd.DataFrame({
        "Roll": ref_rolls,
        "Status": attendance
    })

    attendance_file = os.path.join(output_dir, f"attendance_{uuid.uuid4().hex}.xlsx")
    attendance_df.to_excel(attendance_file, index=False)

    summary = {
        "total": len(ref_rolls),
        "present": attendance.count("P"),
        "absent": attendance.count("A")
    }

    return clean_file, attendance_file, summary
