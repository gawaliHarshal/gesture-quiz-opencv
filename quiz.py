import cv2
import mediapipe as mp
import time

# Quiz Questions and Answers
quiz = [
    {
        "question": "What comes next in the series?\n2, 6, 12, 20, 30, ?",
        "options": ["36", "42", "40", "48"],
        "answer": 2,
        "logic": "Add successive even numbers: +4, +6, +8, +10, +12..."
    },
    {
        "question": "What comes next in the series?\nA, C, F, J, O, ?",
        "options": ["S", "T", "U", "V"],
        "answer": 3,
        "logic": "Positions: +2, +3, +4, +5..."
    },
    {
        "question": "A is the brother of B. B is the mother of C. C is the son of D. How is A related to D?",
        "options": ["Brother-in-law", "Uncle", "Father", "Cousin"],
        "answer": 2,
        "logic": "A is B’s brother → A is C’s uncle → So A is D’s brother-in-law (if D is B’s husband), but assuming traditional relations, 'Uncle' is expected."
    },
    {
        "question": "If APPLE is coded as ELPPA, then how is ORANGE coded?",
        "options": ["EGNARO", "EGNRAO", "EOGNAR", "ENARGO"],
        "answer": 1,
        "logic": "Reverse the word."
    },
    {
        "question": "If 2 + 3 = 13, 3 + 4 = 25, 4 + 5 = 41, then 5 + 6 = ?",
        "options": ["61", "55", "65", "71"],
        "answer": 1,
        "logic": "a + b + (a × b)"
    },
    {
        "question": "Find the odd one out:\n3, 5, 11, 14, 17, 21",
        "options": ["3", "5", "11", "14", "17", "21"],
        "answer": 4,
        "logic": "14 is not a prime number."
    },
    {
        "question": "A person walks 5 km North, then turns right and walks 3 km. Then he turns right and walks 5 km. Where is he from the starting point?",
        "options": ["3 km East", "3 km West", "5 km North", "At starting point"],
        "answer": 1,
        "logic": "Final position is 3 km to the east."
    },
    {
        "question": "Statements:\nAll apples are fruits.\nSome fruits are sweet.\nConclusions:\nI. Some apples are sweet.\nII. All fruits are apples.",
        "options": ["Only I follows", "Only II follows", "Neither I nor II", "Both follow"],
        "answer": 3,
        "logic": "Conclusion I cannot be guaranteed; II is clearly false."
    },
    {
        "question": "If all lions are cats, and some cats are animals, can we say some lions are animals?",
        "options": ["Yes", "No", "Cannot say", "None"],
        "answer": 3,
        "logic": "We cannot infer intersection directly."
    },
    {
        "question": "What is the angle between the hour and minute hand at 3:30?",
        "options": ["60°", "75°", "90°", "105°"],
        "answer": 2,
        "logic": "Angle = |(30*hour - (11/2)*minutes)| = 75°"
    },
    {
        "question": "Pen : Write :: Knife : ?",
        "options": ["Blade", "Cut", "Sharp", "Metal"],
        "answer": 2,
        "logic": "Function of pen is writing, knife is cutting."
    },
    {
        "question": "1, 4, 9, 16, ?, 36",
        "options": ["20", "23", "25", "30"],
        "answer": 3,
        "logic": "Perfect squares: 1², 2², 3², 4², 5², 6²"
    },
    {
        "question": "A man is 24 years older than his son. In 2 years, he will be twice as old. What is the son's current age?",
        "options": ["20", "22", "24", "26"],
        "answer": 2,
        "logic": "Let son's age be x → x + 24 + 2 = 2(x + 2) → x = 22"
    },
    {
        "question": "A, B, C, D, and E are sitting in a row. B is to the right of A but to the left of C. D is at the right end. Who is in the middle?",
        "options": ["A", "B", "C", "D"],
        "answer": 2,
        "logic": "B is in the middle based on the relative positions."
    },
    {
        "question": "If a clock shows 4:45, what is the mirror image?",
        "options": ["7:15", "7:45", "8:15", "8:45"],
        "answer": 1,
        "logic": "Mirror time = 11:60 – 4:45 = 7:15"
    },
    {
        "question": "A cube is painted on all sides and then cut into 27 small cubes. How many cubes have only one face painted?",
        "options": ["6", "12", "8", "9"],
        "answer": 1,
        "logic": "Only 1 center cube per face has one side painted → 6 faces → 6 cubes"
    },
    {
        "question": "Arrange in logical order:\nChild, Teenager, Infant, Adult, Old",
        "options": ["Infant, Child, Teenager, Adult, Old"],
        "answer": 1,
        "logic": "Chronological life stages"
    },
    {
        "question": "Statement: “Use sanitizer to stay safe.”\nAssumption:\nI. People want to stay safe.\nII. Sanitizer keeps people safe.",
        "options": ["Only I", "Only II", "Both", "None"],
        "answer": 3,
        "logic": "Both are implicit assumptions"
    },
    {
        "question": "6 people shake hands with each other once. How many handshakes happen?",
        "options": ["12", "15", "18", "20"],
        "answer": 2,
        "logic": "nC2 = 6C2 = 15"
    },
    {
        "question": "A1, B3, C5, D7, ?",
        "options": ["E8", "E9", "F9", "F11"],
        "answer": 2,
        "logic": "Alphabet +1, Number +2 pattern"
    }
]


# MediaPipe Hand Setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

# OpenCV Camera
cap = cv2.VideoCapture(0)

# Finger tip landmark IDs for detection
finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky

current_question = 0
waiting_for_answer = True
last_answer_time = None
feedback = ""

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)

    finger_count = 0

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            if lm_list:
                finger_count = 0
                for tip_id in finger_tips:
                    if lm_list[tip_id][1] < lm_list[tip_id - 2][1]:  # Finger is open
                        finger_count += 1

    # Display question and options
    q = quiz[current_question]
    cv2.putText(frame, f"Q{current_question + 1}: {q['question']}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    for i, opt in enumerate(q["options"]):
        cv2.putText(frame, f"{i+1}. {opt}", (40, 80 + i*40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 255, 200), 2)

    # Feedback (Correct / Incorrect)
    if feedback:
        cv2.putText(frame, feedback, (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0) if feedback == "Correct!" else (0, 0, 255), 3)

    # Answer checking
    if waiting_for_answer and 1 <= finger_count <= 4:
        if finger_count == q["answer"]:
            feedback = "Correct!"
        else:
            feedback = "Incorrect!"
        waiting_for_answer = False
        last_answer_time = time.time()

    # After showing feedback, move to next question
    if not waiting_for_answer and time.time() - last_answer_time > 2:
        current_question += 1
        feedback = ""
        waiting_for_answer = True
        if current_question >= len(quiz):
            break  # End quiz

    cv2.imshow("Quiz with Hand Gestures", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
