import os
# os.environ["OPEN3D_CPU_RENDERING"] = "true"
import open3d as o3d
import numpy as np

# 1. Read the OBJ file
mesh = o3d.io.read_triangle_mesh("data/CUBE.obj")

# 2. Extract vertices
vertices = np.asarray(mesh.vertices)

# 3. Print basic info
print("Total vertices:", vertices.shape[0])
print("Vertex array shape:", vertices.shape)

# 4. Print first 5 vertices
print("\nFirst 5 vertices:")
print(vertices[:5])

# 5. Print min/max values along each axis
print("\nMin values (X, Y, Z):", vertices.min(axis=0))
print("Max values (X, Y, Z):", vertices.max(axis=0))

# 6. Compute centroid
centroid = vertices.mean(axis=0)
print("\nCentroid (mean X, Y, Z):", centroid)

# 7. Center the point cloud
vertices_centered = vertices - centroid

# 8. Verify centering
print("\nAfter centering:")
print("Min values:", vertices_centered.min(axis=0))
print("Max values:", vertices_centered.max(axis=0))
print("Mean values (should be ~0):", vertices_centered.mean(axis=0))

# =======================
# PCA COMPUTATION
# =======================

# 9. Compute covariance matrix (3x3)
covariance_matrix = np.cov(vertices_centered.T)
print("\nCovariance Matrix:\n", covariance_matrix)

# 10. Eigen decomposition
eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

# 11. Sort eigenvalues & eigenvectors (descending order)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

print("\nEigenvalues (descending):")
print(eigenvalues)

print("\nEigenvectors (columns = PC1, PC2, PC3):")
print(eigenvectors)


# =======================
# ROTATE POINT CLOUD INTO PCA FRAME
# =======================

# 12. Rotate centered points into PCA coordinate system
# (Transpose because eigenvectors are column-wise)
points_pca = vertices_centered @ eigenvectors

# 13. Compute min & max in PCA frame
min_pca = points_pca.min(axis=0)
max_pca = points_pca.max(axis=0)

length, width, height = max_pca - min_pca

print("\nPCA-aligned min values:", min_pca)
print("PCA-aligned max values:", max_pca)

print("\nOBB Dimensions (L, W, H):")
print(f"Length: {length:.4f}")
print(f"Width : {width:.4f}")
print(f"Height: {height:.4f}")

# 14. Volume of Oriented Bounding Box
volume = length * width * height
print(f"\nOBB Volume: {volume:.4f}")


# =======================
# OBB VISUALIZATION
# =======================

# 15. Create Open3D mesh again (for visualization)
mesh = o3d.io.read_triangle_mesh("data/CUBE.obj")
mesh.compute_vertex_normals()
mesh.paint_uniform_color([0.7, 0.7, 0.7])  # light gray

# 16. Create Oriented Bounding Box
obb = o3d.geometry.OrientedBoundingBox()

# Center of box in world coordinates
obb.center = centroid

# Rotation matrix (columns are principal axes)
obb.R = eigenvectors

# Extent = dimensions of box
obb.extent = np.array([length, width, height])

# Set OBB color (red)
obb.color = (1, 0, 0)

# 17. Visualize mesh + OBB
vis = o3d.visualization.Visualizer()
vis.create_window(window_name="OBB", width=1024, height=768, visible=True)
vis.add_geometry(mesh)
vis.add_geometry(obb)
vis.run()
vis.destroy_window()
