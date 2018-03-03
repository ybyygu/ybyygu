// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::34ebf4ed-5677-4f45-bb0c-4d8fb22bc514][34ebf4ed-5677-4f45-bb0c-4d8fb22bc514]]
use std::error::Error;
use cgmath::prelude::*;
use std::io::{self, BufReader};
use std::io::prelude::*;
use std::fs::File;

fn get_positions_from_xyz_stream(txt: &str) -> Result<Vec<[f64; 3]>, Box<Error>> {
    let mut positions = Vec::new();

    for line in txt.lines() {
        let attrs: Vec<_> = line.split_whitespace().collect();
        let (symbol, position) = attrs.split_first().ok_or("encountering empty line")?;
        if position.len() != 3 {
            let msg = format!("informal xyz records: {}", line);
            Err(msg)?;
        }

        let p: Vec<f64> = position.iter().map(|x| x.parse().unwrap()).collect();
        positions.push([p[0], p[1], p[2]]);
    }

    Ok(positions)
}

// in a simple and dirty way
fn get_positions_from_xyzfile(filename: &str) -> Result<Vec<[f64; 3]>, Box<Error>> {
    let mut buffer = String::new();
    let f = File::open(filename)?;
    let mut f = BufReader::new(f);

    f.read_line(&mut buffer);
    f.read_line(&mut buffer);
    buffer.clear();

    f.read_to_string(&mut buffer)?;
    get_positions_from_xyz_stream(&buffer)
}
// 34ebf4ed-5677-4f45-bb0c-4d8fb22bc514 ends here

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

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::2d2b9c1f-4f35-4939-9410-31d3a7213b21][2d2b9c1f-4f35-4939-9410-31d3a7213b21]]
#[derive(Debug, Clone)]
struct Octant {
    center: [f64; 3],
    extent: f64,
    ipoints: Vec<usize>,         // indices of the points in a public array
}

impl Octant {
    fn new(extent: f64) -> Self {
        Octant {
            center: [0.0; 3],
            extent: extent,
            ipoints: vec![],
        }
    }
}

#[derive(Debug)]
struct Query {
    center : [f64; 3],
    radius : f64,
}

impl Query {
    fn new(r: f64) -> Self {
        Query {
            center : [0.0; 3],
            radius : r,
        }
    }

    /// test if there is overlapping between query ball and the octant
    fn is_overlap(&self, octant: &Octant) -> bool {
        let x = (self.center[0] - octant.center[0]).abs();
        let y = (self.center[1] - octant.center[1]).abs();
        let z = (self.center[2] - octant.center[2]).abs();

        let extent = octant.extent;
        let max_dist = extent + self.radius;

        // case 1: > e+r
        if (x > max_dist || y > max_dist || z > max_dist) {
            // println!("{:?}", "case 1");
            return false;
        }

        // case 2: < e
        if (x < extent || y < extent || z < extent) {
            // println!("{:?}", "case 2");
            return true;
        }

        // case 3: between e and e+r
        let nx = x - extent;
        let ny = y - extent;
        let nz = z - extent;

        assert!(nx > 0., nx);
        assert!(ny > 0., ny);
        assert!(nz > 0., nz);

        // println!("d = {:?}", nx*nx+ny*ny+nz*nz);
        nx*nx + ny*ny + nz*nz < self.radius*self.radius
    }

    /// test if if the octant is completely contained by the query ball
    fn is_contains(&self, octant: &Octant) -> bool {
        let extent = octant.extent;
        let x = (self.center[0] - octant.center[0]).abs() + extent;
        let y = (self.center[1] - octant.center[1]).abs() + extent;
        let z = (self.center[2] - octant.center[2]).abs() + extent;

        x*x + y*y + z*z < self.radius*self.radius
    }
}
// 2d2b9c1f-4f35-4939-9410-31d3a7213b21 ends here

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::96cefae3-a99f-4f6b-823f-2f89f98824fa][96cefae3-a99f-4f6b-823f-2f89f98824fa]]
fn octant_from_points(points: &Vec<[f64; 3]>) -> Octant {
    let mut p_min = points[0];
    let mut p_max = points[0];

    for p in points {
        if p[0] > p_max[0] {
            p_max[0] = p[0];
        } else if p[0] < p_min[0] {
            p_min[0] = p[0];
        }

        if p[1] > p_max[1] {
            p_max[1] = p[1];
        } else if p[1] < p_min[1] {
            p_min[1] = p[1];
        }

        if p[2] > p_max[2] {
            p_max[2] = p[2];
        } else if p[2] < p_min[2] {
            p_min[2] = p[2];
        }
    }

    let mut pe = [p_max[0] - p_min[0], p_max[1] - p_min[1], p_max[2] - p_min[2]];
    let mut extent = 0.;
    for &v in pe.iter() {
        if v > extent {
            extent = v;
        }
    }

    let mut octant = Octant::new(extent/2.);
    octant.center = [(p_max[0] + p_min[0])/2., (p_max[1] + p_min[1])/2., (p_max[2] + p_min[2])/2.,];

    let n = points.len();
    octant.ipoints = (0..n).collect();

    octant
}

#[test]
fn test_octree_init() {
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
 H                 -0.03366507   -7.86361434   -3.37298245 ";

    let points = get_positions_from_xyz_stream(&txt).unwrap();
    let octant = octant_from_points(&points);
    assert_relative_eq!(octant.center[0], 0.103126, epsilon=1e-4);
    assert_relative_eq!(octant.center[1], -5.717873145, epsilon=1e-4);
    assert_relative_eq!(octant.center[2], -2.75229595, epsilon=1e-4);
    assert_relative_eq!(octant.extent, 2.145741195, epsilon=1e-4);
}
// 96cefae3-a99f-4f6b-823f-2f89f98824fa ends here

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::9db18239-7b01-48a3-aedc-7bcc082e7949][9db18239-7b01-48a3-aedc-7bcc082e7949]]
use indextree::Arena;

// octant: octree node
// points: points in 3D space for reference
fn octree_create_octants(octant: &Octant, points: &Vec<[f64; 3]>) {
    // Create a new arena
    let arena = &mut Arena::new();

    // a: parent octant
    let a = arena.new_node(octant.clone());

    if octant.ipoints.len() > 1 {
        let mut parent = a;
        let mut current = octant;
        loop {
            // add child octants to the parent octant
            for o in octree_create_child_octants(current, points) {
                let b = arena.new_node(o);
                parent.append(b, arena);
            }

            for x in parent.children(arena) {
                println!("{:?}", x);
            }
            break;
        }
    }

    println!("{:?}", arena);
}

// octant: octree node
// points: points in 3D space for reference
fn octree_create_child_octants(octant: &Octant, points: &Vec<[f64; 3]>) -> Vec<Octant> {
    let extent = octant.extent / 2.;

    let mut cells = vec![];

    // initialize 8 child octants
    for i in 0..8 {
        let mut o = Octant::new(extent);
        let factors = get_octant_cell_factor(i);
        for j in 0..3 {
            o.center[j] += 0.5*extent*factors[j] + octant.center[j]
        }
        cells.push(o);
    }

    if octant.ipoints.len() > 1 {
        let (x0, y0, z0) = (octant.center[0], octant.center[1], octant.center[2]);
        // 1. scan xyz
        for &i in octant.ipoints.iter() {
            let p = points[i];
            let (x, y, z) = (p[0] - x0, p[1] - y0, p[2] - z0);
            let index = get_octant_cell_index(x, y, z);
            cells[index].ipoints.push(i);
        }
    }

    let mut octant = Octant::new(extent);
    for (i, ref cell) in cells.iter().enumerate() {
        println!("{:?}", (i, cell));
    }

    cells
}

// zyx: +++ => 0
// zyx: ++- => 1
// zyx: --- => 7
fn get_octant_cell_index(x: f64, y: f64, z: f64) -> usize {
    let bits = [z.is_sign_negative(), y.is_sign_negative(), x.is_sign_negative()];
    bits.iter().fold(0, |acc, &b| acc*2 + b as usize)
}

#[test]
fn test_octree_cell_index() {
    let index = get_octant_cell_index(1.0, 1.0, 1.0);
    assert_eq!(index, 0);

    let index = get_octant_cell_index(-1.0, -1.0, -1.0);
    assert_eq!(index, 7);

    let index = get_octant_cell_index(-1.0, 1.0, 1.0);
    assert_eq!(index, 1);

    let index = get_octant_cell_index(-1.0, -1.0, 1.0);
    assert_eq!(index, 3);
}

// useful for calculate center of child octant
fn get_octant_cell_factor(index: usize) -> [f64; 3] {
    debug_assert!(index < 8 && index >= 0);
    [
        match (index & 0b001) == 0 {
            true => 1.0,
            false => -1.0,
        },
        match ((index & 0b010) >> 1) == 0 {
            true => 1.0,
            false => -1.0,
        },
        match ((index & 0b100) >> 2) == 0 {
            true => 1.0,
            false => -1.0,
        }
    ]
}

#[test]
fn test_octree_factor() {
    let x = get_octant_cell_factor(0);
    assert_eq!(1.0, x[0]);
    assert_eq!(1.0, x[1]);
    assert_eq!(1.0, x[2]);

    let x = get_octant_cell_factor(7);
    assert_eq!(-1.0, x[0]);
    assert_eq!(-1.0, x[1]);
    assert_eq!(-1.0, x[2]);

    let x = get_octant_cell_factor(2);
    assert_eq!(1.0, x[0]);
    assert_eq!(-1.0, x[1]);
    assert_eq!(1.0, x[2]);
}

#[test]
fn test_octree() {
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
 H                 -0.03366507   -7.86361434   -3.37298245 ";

    let points = get_positions_from_xyz_stream(&txt).unwrap();
    let octant = octant_from_points(&points);
    let children = octree_create_child_octants(&octant, &points);
    let child = &children[0];
    let x = child.center[0] - octant.center[0];
    let y = child.center[1] - octant.center[1];
    let z = child.center[2] - octant.center[2];
    assert_relative_eq!(x, y, epsilon=1e-4);
    assert_relative_eq!(x, z, epsilon=1e-4);

    assert_eq!(octant.extent, child.extent * 2.0);
    assert_eq!(x, child.extent * 0.5);

    let child = &children[1];
    let x = child.center[0] - octant.center[0];
    let y = child.center[1] - octant.center[1];
    let z = child.center[2] - octant.center[2];
    assert_relative_eq!(x, child.extent * -0.5, epsilon=1e-4);
    assert_relative_eq!(y, child.extent * 0.5, epsilon=1e-4);
    assert_relative_eq!(z, child.extent * 0.5, epsilon=1e-4);

    assert!(children[7].ipoints.contains(&2));

    octree_create_octants(&octant, &points);
}
// 9db18239-7b01-48a3-aedc-7bcc082e7949 ends here

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::81167b8a-bac9-4a8e-a6c9-56e48dcd6e79][81167b8a-bac9-4a8e-a6c9-56e48dcd6e79]]
#[test]
fn test_overlap() {
    let octant = Octant::new(2.5);
    let mut query = Query::new(0.4);
    query.center = [2.7, 2.7, 2.7];
    assert!(query.is_overlap(&octant));
    query.center = [2.7, -2.7, -2.7];
    assert!(query.is_overlap(&octant));
    query.center = [2.8, 2.8, 2.8];
    assert!(!query.is_overlap(&octant));
}

#[test]
fn test_contains() {
    let octant = Octant::new(2.5);
    let mut query = Query::new(1.4);
    assert!(!query.is_contains(&octant));

    query.radius = 4.4;         // 2.5*sqrt(3)
    let x = query.is_contains(&octant);
    assert!(query.is_contains(&octant));
}
// 81167b8a-bac9-4a8e-a6c9-56e48dcd6e79 ends here
