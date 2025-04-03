use convlog::tenhou::Log;

fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    if args.len() != 2 {
        eprintln!("Usage: {} <path to log file>", args[0]);
        std::process::exit(1);
    }
    let path = &args[1];
    match Log::from_json_str(&std::fs::read_to_string(path).unwrap()) {
        Ok(_) => println!("Ok"),
        Err(e) => eprintln!("Error reading log file: {}", e),
    }
}
