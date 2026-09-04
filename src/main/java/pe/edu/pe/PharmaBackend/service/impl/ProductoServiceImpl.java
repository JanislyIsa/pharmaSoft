package pe.edu.pe.PharmaBackend.service.impl;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.pe.PharmaBackend.dto.CategoriaResumenDTO;
import pe.edu.pe.PharmaBackend.dto.ProductoRequestDTO;
import pe.edu.pe.PharmaBackend.dto.ProductoResponseDTO;
import pe.edu.pe.PharmaBackend.entity.Categoria;
import pe.edu.pe.PharmaBackend.entity.Producto;
import pe.edu.pe.PharmaBackend.exception.RecursoNoEncontradoException;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.repository.CategoriaRepository;
import pe.edu.pe.PharmaBackend.repository.ProductoRepository;
import pe.edu.pe.PharmaBackend.service.service.ProductoService;

@Service
public class ProductoServiceImpl implements ProductoService {
    private static final Logger LOG = LoggerFactory.getLogger(ProductoServiceImpl.class);
    private final ProductoRepository productoRepository;
    private final CategoriaRepository categoriaRepository;

    public ProductoServiceImpl(ProductoRepository productoRepository, CategoriaRepository categoriaRepository){
        this.productoRepository = productoRepository;
        this.categoriaRepository = categoriaRepository;
    }

    @Override
    @Transactional
    public ProductoResponseDTO create(ProductoRequestDTO t) {
        String nombre = t.getNombre().trim();
        if (productoRepository.existsByNombreIgnoreCase(nombre)){
            throw new ReglaNegocioException("Ya existe un producto con el nombre " + nombre);
        }
        Producto producto = new Producto();
        producto.setNombre(nombre);
        producto.setPrecio(t.getPrecio());
        producto.setStock(t.getStock());
        producto.setCategoria(buscarCategoriaPorId(t.getCategoriaId()));
        Producto prodCreada = productoRepository.save(producto);
        LOG.info("Producto creado con id={}", prodCreada.getId());
        return convertirResponse(prodCreada);
    }

    private Categoria buscarCategoriaPorId(Long id) {
        return categoriaRepository.findById(id)
                .orElseThrow(() -> new RecursoNoEncontradoException("Categoría no encontrada con id: " + id));
    }

    @Override
    @Transactional
    public ProductoResponseDTO update(Long aLong, ProductoRequestDTO t) {
        Producto producto = productoRepository.findById(aLong).orElseThrow(() ->
                new RecursoNoEncontradoException("Producto no encontrado con id: " + aLong));

        producto.setNombre(t.getNombre());
        producto.setPrecio(t.getPrecio());
        producto.setStock(t.getStock());
        producto.setCategoria(buscarCategoriaPorId(t.getCategoriaId()));

        Producto prodActualizada = productoRepository.save(producto);
        LOG.info("Producto id={} actualizado", prodActualizada.getId());
        return convertirResponse(prodActualizada);
    }

    @Override
    @Transactional(readOnly = true)
    public ProductoResponseDTO read(Long aLong) {
        Producto producto = productoRepository.findById(aLong)
                .orElseThrow(() -> new RecursoNoEncontradoException("Producto no encontrado con id: " + aLong));
        return convertirResponse(producto);
    }

    @Override
    @Transactional
    public void delete(Long aLong) {
        Producto producto = productoRepository.findById(aLong).orElseThrow(() ->
                new RecursoNoEncontradoException("Producto no encontrado con id: " + aLong));
        productoRepository.delete(producto);
        LOG.info("Producto id={} eliminado", aLong);
    }

    @Override
    @Transactional(readOnly = true)
    public Iterable<ProductoResponseDTO> readAll() {
        return productoRepository.findAll()
                .stream()
                .map(this::convertirResponse)
                .toList();
    }

    private ProductoResponseDTO convertirResponse(Producto producto){
        CategoriaResumenDTO categoriaResumen = producto.getCategoria() != null
                ? new CategoriaResumenDTO(producto.getCategoria().getId(), producto.getCategoria().getNombre())
                : null;

        return new ProductoResponseDTO(
                producto.getId(),
                producto.getNombre(),
                producto.getPrecio(),
                producto.getStock(),
                producto.getEstado(),
                categoriaResumen,
                producto.getFechaCreacion(),
                producto.getFechaModificacion()
        );
    }
}