use std::fs::File;
use std::io::Read;

use byteorder::{LittleEndian, ReadBytesExt};
use std::io::Cursor;

#[allow(non_snake_case)]
#[derive(Debug)]
struct BmpFileHeader {
    bfType: [u8; 2],
    bfSize: u32,
    bfReserved1: u16,
    bfReserved2: u16,
    bfOffBits: u32,
}

#[allow(non_snake_case)]
impl BmpFileHeader {
    fn parse_file_header(buf: &[u8]) -> std::io::Result<BmpFileHeader> {
        let mut cur = Cursor::new(buf);
        let mut bfType = [0_u8; 2];
        for cc in &mut bfType {
            *cc = cur.read_u8()?;
        }

        let bfSize = cur.read_u32::<LittleEndian>()?;
        let bfReserved1 = cur.read_u16::<LittleEndian>()?;
        let bfReserved2 = cur.read_u16::<LittleEndian>()?;
        let bfOffBits = cur.read_u32::<LittleEndian>()?;

        Ok(BmpFileHeader {
            bfType,
            bfSize,
            bfReserved1,
            bfReserved2,
            bfOffBits,
        })
    }
}

fn main() -> std::io::Result<()> {
    let mut f = File::open("input.bmp")?;
    let mut buf_file_header = [0_u8; 14];

    let _ = f.read(&mut buf_file_header)?;

    let file_header = BmpFileHeader::parse_file_header(&buf_file_header)?;

    println!("{:?}", file_header);
    Ok(())
}
