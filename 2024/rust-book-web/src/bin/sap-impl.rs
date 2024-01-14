struct TestResult {
    passed: bool,
    message: String,
}

impl TestResult {
    fn new(passed: bool, message: String) -> TestResult {
        TestResult { passed, message }
    }

    fn passed(&self) -> bool {
        self.passed
    }
}

fn main() {
    let test_res = TestResult::new(true, "This test failed!".to_string());
    if test_res.passed() {
        println!("The test passed!");
    } else {
        println!("The test failed: {}", test_res.message);
    }
}
