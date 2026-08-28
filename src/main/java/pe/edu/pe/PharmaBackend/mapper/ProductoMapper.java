package pe.edu.pe.PharmaBackend.mapper;

import org.springframework.stereotype.Component;
import pe.edu.pe.PharmaBackend.dto.CategoriaResumenDTO;
import pe.edu.pe.PharmaBackend.dto.ProductoRequestDTO;
import pe.edu.pe.PharmaBackend.dto.ProductoResponseDTO;
import pe.edu.pe.PharmaBackend.entity.Categoria;
import pe.edu.pe.PharmaBackend.entity.Producto;

@Component
public class ProductoMapper {

    public Producto toEntity(ProductoRequestDTO dto, Categoria categoria) {
        Producto producto = new Producto();
        producto.setNombre(dto.getNombre().trim());
        producto.setPrecio(dto.getPrecio());
        producto.setStock(dto.getStock());
        producto.setCategoria(categoria);
        return producto;
    }

    public void actualizarEntity(Producto producto, ProductoRequestDTO dto, Categoria categoria) {
        producto.setNombre(dto.getNombre().trim());
        producto.setPrecio(dto.getPrecio());
        producto.setStock(dto.getStock());
        producto.setCategoria(categoria);
    }

    public ProductoResponseDTO toResponseDTO(Producto producto) {
        return new ProductoResponseDTO(
                producto.getId(),
                producto.getNombre(),
                producto.getPrecio(),
                producto.getStock(),
                producto.getEstado(),
                new CategoriaResumenDTO(producto.getCategoria().getId(), producto.getCategoria().getNombre()),
                producto.getFechaCreacion(),
                producto.getFechaModificacion()
        );
    }
}