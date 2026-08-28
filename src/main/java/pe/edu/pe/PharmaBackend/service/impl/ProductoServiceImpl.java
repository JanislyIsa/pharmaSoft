package pe.edu.pe.PharmaBackend.service.impl;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.pe.PharmaBackend.dto.ProductoRequestDTO;
import pe.edu.pe.PharmaBackend.dto.ProductoResponseDTO;
import pe.edu.pe.PharmaBackend.entity.Categoria;
import pe.edu.pe.PharmaBackend.entity.Producto;
import pe.edu.pe.PharmaBackend.exception.RecursoNoEncontradoException;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.mapper.ProductoMapper;
import pe.edu.pe.PharmaBackend.repository.CategoriaRepository;
import pe.edu.pe.PharmaBackend.repository.ProductoRepository;
import pe.edu.pe.PharmaBackend.service.service.ProductoService;

import java.util.Optional;

@Service
public class ProductoServiceImpl implements ProductoService {

    private static final Logger LOG = LoggerFactory.getLogger(ProductoServiceImpl.class);

    private final ProductoRepository productoRepository;
    private final CategoriaRepository categoriaRepository;
    private final ProductoMapper productoMapper;

    public ProductoServiceImpl(ProductoRepository productoRepository,
                               CategoriaRepository categoriaRepository,
                               ProductoMapper productoMapper) {
        this.productoRepository = productoRepository;
        this.categoriaRepository = categoriaRepository;
        this.productoMapper = productoMapper;
    }

    @Override
    @Transactional
    public ProductoResponseDTO create(ProductoRequestDTO t) {
        LOG.info("Creando producto '{}' con categoriaId={}", t.getNombre(), t.getCategoriaId());
        Categoria categoria = obtenerCategoriaValida(t.getCategoriaId());

        String nombre = t.getNombre().trim();
        if (productoRepository.existsByNombreIgnoreCase(nombre)) {
            LOG.warn("Intento de crear producto duplicado: {}", nombre);
            throw new ReglaNegocioException("El nombre de producto ya existe en el sistema: " + nombre);
        }

        Producto producto = productoMapper.toEntity(t, categoria);
        Producto creado = productoRepository.save(producto);
        LOG.info("Producto creado con id={}, estado={} (stock={}), categoria id={}",
                creado.getId(), creado.getEstado(), creado.getStock(), categoria.getId());
        return productoMapper.toResponseDTO(creado);
    }

    @Override
    @Transactional
    public ProductoResponseDTO update(Long id, ProductoRequestDTO t) {
        LOG.info("Actualizando producto id={}", id);
        Producto producto = productoRepository.findById(id).orElseThrow(() ->
                new RecursoNoEncontradoException("Producto no encontrado con el id: " + id));

        Categoria categoria = obtenerCategoriaValida(t.getCategoriaId());

        String nombre = t.getNombre().trim();
        if (productoRepository.existsByNombreIgnoreCaseAndIdNot(nombre, id)) {
            LOG.warn("Nombre duplicado al actualizar producto id={}: {}", id, nombre);
            throw new ReglaNegocioException("El nombre de producto ya existe en el sistema: " + nombre);
        }

        productoMapper.actualizarEntity(producto, t, categoria);
        Producto actualizado = productoRepository.save(producto);
        LOG.info("Producto id={} actualizado, nuevo estado={} (stock={})",
                actualizado.getId(), actualizado.getEstado(), actualizado.getStock());
        return productoMapper.toResponseDTO(actualizado);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<ProductoResponseDTO> read(Long id) {
        LOG.info("Consultando producto id={}", id);
        return productoRepository.findById(id).map(productoMapper::toResponseDTO);
    }

    @Override
    @Transactional
    public void delete(Long id) {
        LOG.info("Eliminando producto id={}", id);
        Producto producto = productoRepository.findById(id).orElseThrow(() ->
                new RecursoNoEncontradoException("Producto no encontrado con el id: " + id));
        productoRepository.delete(producto);
        LOG.info("Producto id={} eliminado correctamente", id);
    }

    @Override
    @Transactional(readOnly = true)
    public Iterable<ProductoResponseDTO> readAll() {
        LOG.info("Consultando listado completo de productos");
        return productoRepository.findAll().stream().map(productoMapper::toResponseDTO).toList();
    }

    private Categoria obtenerCategoriaValida(Long categoriaId) {
        return categoriaRepository.findById(categoriaId).orElseThrow(() -> {
            LOG.warn("Referencia inválida: no existe categoria con id={}", categoriaId);
            return new RecursoNoEncontradoException("La categoría con id " + categoriaId + " no existe");
        });
    }
}