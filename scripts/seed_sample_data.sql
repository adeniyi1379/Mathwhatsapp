-- Seed sample data for SolveWithMe platform

-- Insert sample schools (pilot program)
INSERT INTO schools (name, location, contact_person, contact_phone, is_pilot_school) VALUES
('Government Secondary School Ikeja', 'Ikeja, Lagos', 'Mr. Adebayo Johnson', '+2348012345678', true),
('Federal Government College Warri', 'Warri, Delta', 'Mrs. Ngozi Okafor', '+2348023456789', true),
('Government College Keffi', 'Keffi, Nasarawa', 'Malam Ibrahim Sani', '+2348034567890', true);

-- Insert sample WAEC/JAMB questions
INSERT INTO exam_questions (question_text, answer_text, explanation, source, year, topic, difficulty_level) VALUES
(
    'Solve for x: 2x + 5 = 13',
    'x = 4',
    'Step 1: Subtract 5 from both sides: 2x = 8. Step 2: Divide both sides by 2: x = 4',
    'WAEC',
    2023,
    'Linear Equations',
    'Easy'
),
(
    'Find the area of a circle with radius 7cm (Take π = 22/7)',
    '154 cm²',
    'Area = πr² = (22/7) × 7² = (22/7) × 49 = 22 × 7 = 154 cm²',
    'JAMB',
    2023,
    'Geometry - Circles',
    'Medium'
),
(
    'Factorize completely: x² - 9',
    '(x + 3)(x - 3)',
    'This is a difference of two squares: a² - b² = (a + b)(a - b). Here, x² - 9 = x² - 3² = (x + 3)(x - 3)',
    'WAEC',
    2022,
    'Algebra - Factorization',
    'Easy'
),
(
    'If log₂ 8 = x, find the value of x',
    'x = 3',
    'log₂ 8 = x means 2ˣ = 8. Since 2³ = 8, therefore x = 3',
    'JAMB',
    2023,
    'Logarithms',
    'Medium'
),
(
    'Find the gradient of the line joining points A(2, 3) and B(6, 11)',
    '2',
    'Gradient = (y₂ - y₁)/(x₂ - x₁) = (11 - 3)/(6 - 2) = 8/4 = 2',
    'WAEC',
    2023,
    'Coordinate Geometry',
    'Medium'
),
(
    'Simplify: 3√18 - 2√8 + √32',
    '11√2',
    '3√18 = 3√(9×2) = 3×3√2 = 9√2; 2√8 = 2√(4×2) = 2×2√2 = 4√2; √32 = √(16×2) = 4√2. Therefore: 9√2 - 4√2 + 4√2 = 9√2',
    'JAMB',
    2022,
    'Surds',
    'Hard'
),
(
    'A bag contains 5 red balls and 3 blue balls. What is the probability of picking a red ball?',
    '5/8',
    'Total balls = 5 + 3 = 8. Probability of red = Number of red balls / Total balls = 5/8',
    'WAEC',
    2023,
    'Probability',
    'Easy'
),
(
    'Find the value of x if 3ˣ = 27',
    'x = 3',
    '3ˣ = 27. Since 27 = 3³, we have 3ˣ = 3³. Therefore x = 3',
    'JAMB',
    2023,
    'Indices',
    'Easy'
);

-- Insert sample users (for testing)
INSERT INTO users (phone_number, name, school, grade_level, preferred_language) VALUES
('+2348012345001', 'Adebayo Ogundimu', 'Government Secondary School Ikeja', 'SS2', 'english'),
('+2348023456002', 'Fatima Abdullahi', 'Government College Keffi', 'SS3', 'hausa'),
('+2348034567003', 'Chioma Okwu', 'Federal Government College Warri', 'SS1', 'igbo'),
('+2348045678004', 'Tunde Adeyemi', 'Government Secondary School Ikeja', 'SS2', 'yoruba');

-- Insert sample teacher moderators
INSERT INTO teacher_moderators (user_id, school_id, subject_specialization) VALUES
(1, 1, 'Mathematics'),
(2, 3, 'Mathematics and Physics'),
(3, 2, 'Mathematics and Chemistry');
