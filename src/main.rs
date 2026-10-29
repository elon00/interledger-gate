/// Exact-integer offline transfer invariant only; not ILP or live settlement.
fn apply_transfer(source: u64, destination: u64, amount: u64) -> Result<(u64, u64), &'static str> {
    if amount == 0 {
        return Err("INVALID_AMOUNT");
    }
    let source = source.checked_sub(amount).ok_or("INSUFFICIENT_FUNDS")?;
    let destination = destination.checked_add(amount).ok_or("BALANCE_OVERFLOW")?;
    Ok((source, destination))
}

fn main() {
    match apply_transfer(100, 0, 25) {
        Ok((source, destination)) if source + destination == 100 => {
            println!("PASS: offline balance conservation only; no RPC, PQC or settlement");
        }
        _ => {
            eprintln!("FAIL: offline invariant");
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_conservation() {
        assert_eq!(apply_transfer(100, 10, 25), Ok((75, 35)));
    }

    #[test]
    fn rejects_invalid_and_overflow() {
        assert_eq!(apply_transfer(1, 0, 2), Err("INSUFFICIENT_FUNDS"));
        assert_eq!(apply_transfer(1, 0, 0), Err("INVALID_AMOUNT"));
        assert_eq!(apply_transfer(2, u64::MAX, 1), Err("BALANCE_OVERFLOW"));
    }
}
