// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::34ebf4ed-5677-4f45-bb0c-4d8fb22bc514][34ebf4ed-5677-4f45-bb0c-4d8fb22bc514]]
use std::error::Error;
use cgmath::prelude::*;
use cgmath::Point3;

fn get_neighbors(positions: &Vec<Point3<f64>>, p: Point3<f64>) {
    println!("{:?}", positions[0].x);

    let p1 = [0.0; 3];
    let px = Point3::from(p1);
    println!("{:?}", px);

    for &x in positions {
        println!("{:?}", p.distance(x));
    }
}

fn get_positions_from_xyz_stream(txt: &str) -> Result<Vec<Point3<f64>>, Box<Error>> {
    let mut positions = Vec::new();

    for line in txt.lines() {
        let attrs: Vec<_> = line.split_whitespace().collect();
        let (symbol, position) = attrs.split_first().ok_or("encountering empty line")?;
        if position.len() != 3 {
            let msg = format!("informal xyz records: {}", line);
            Err(msg)?;
        }

        let p: Vec<f64> = position.iter().map(|x| x.parse().unwrap()).collect();
        positions.push(Point3::new(p[0], p[1], p[2]));
    }

    Ok(positions)
}
// 34ebf4ed-5677-4f45-bb0c-4d8fb22bc514 ends here

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::cd993c57-2284-473c-b6cd-2edbe095530b][cd993c57-2284-473c-b6cd-2edbe095530b]]
#[test]
fn test_cgmath() {
    let txt = " N                  0.49180679   -7.01280337   -3.37298245
 H                  1.49136679   -7.04246937   -3.37298245
 C                 -0.19514721   -5.73699137   -3.37298245
 H                 -0.81998021   -5.66018837   -4.26280545
 C                 -1.08177021   -5.59086937   -2.14084145
 C                  0.79533179   -4.58138037   -3.37298245
 H                 -0.46899721   -5.65651737   -1.24178645
 H                 -1.58492621   -4.62430837   -2.16719845
 H                 -1.82600521   -6.38719137   -2.13160945
 O                  2.03225779   -4.81286537   -3.37298245
 H                  0.43991988   -3.57213195   -3.37298245
 H                 -0.03366507   -7.86361434   -3.37298245
";
    let positions = get_positions_from_xyz_stream(&txt).unwrap();

    get_neighbors(&positions, positions[0]);
}
// cd993c57-2284-473c-b6cd-2edbe095530b ends here
