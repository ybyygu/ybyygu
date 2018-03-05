// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::ebfcba82-f6fc-4675-85d0-a6bd11aa1880][ebfcba82-f6fc-4675-85d0-a6bd11aa1880]]
use std::error::Error;

use neighbors::get_positions_from_xyz_stream;
use neighbors::get_positions_from_xyzfile;
// ebfcba82-f6fc-4675-85d0-a6bd11aa1880 ends here

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::6d08c39d-a937-462a-ba39-4c2855bf121d][6d08c39d-a937-462a-ba39-4c2855bf121d]]
fn get_neighbors_naive(positions: &Vec<[f64; 3]>,
                       p: [f64; 3], cutoff: f64) -> Vec<(usize, f64)>
{
    let r2 = cutoff*cutoff;

    let mut neighbors = Vec::new();
    let (x0, y0, z0) = (p[0], p[1], p[2]);
    for (i, &p) in positions.iter().enumerate() {
        let (dx, dy, dz) = (p[0]-x0, p[1]-y0, p[2]-z0);
        let d2 = dx*dx + dy*dy + dz*dz;
        if d2 <= r2 {
            neighbors.push((i, d2.sqrt()));
        }
    }

    neighbors
}
// 6d08c39d-a937-462a-ba39-4c2855bf121d ends here

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::b9783b68-dd07-42d5-ae7b-901c13cbaa9d][b9783b68-dd07-42d5-ae7b-901c13cbaa9d]]
fn get_neighbors_smart(positions: &Vec<[f64; 3]>,
                       p: [f64; 3], cutoff: f64) -> Vec<(usize, f64)>
{
    let r2 = cutoff*cutoff;

    let mut neighbors = vec![];
    let (x0, y0, z0) = (p[0], p[1], p[2]);
    for (i, &po) in positions.iter().enumerate() {
        let dx = (po[0] - x0);
        let dy = (po[1] - y0);
        let dz = (po[2] - z0);
        if dx.abs() > cutoff {
            continue;
        }
        if dy.abs() > cutoff {
            continue;
        }
        if dz.abs() > cutoff {
            continue;
        }

        let d2 = dx*dx + dy*dy + dz*dz;
        if d2 <= r2 {
            neighbors.push((i, d2.sqrt()));
        }
    }

    neighbors
}
// b9783b68-dd07-42d5-ae7b-901c13cbaa9d ends here

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::cd993c57-2284-473c-b6cd-2edbe095530b][cd993c57-2284-473c-b6cd-2edbe095530b]]
#[test]
fn test_linear() {
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

    // large xyz file
    let xyzfile = "/home/ybyygu/Workspace/Programming/chem-utils/data/51/226f67-055e-42a6-a88d-771f78d7d48e/pdb4rhv.xyz";
    let positions = get_positions_from_xyzfile(xyzfile).unwrap();

    timeit!({
        for &p in positions.iter() {
            get_neighbors_naive(&positions, p, 3.0);
        }
    });

    timeit!({
        for &p in positions.iter() {
            get_neighbors_smart(&positions, p, 3.0);
        }
    });
}
// cd993c57-2284-473c-b6cd-2edbe095530b ends here
