package pe.edu.pe.PharmaBackend.service.impl;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.pe.PharmaBackend.dto.CategoriaRequestDTO;
import pe.edu.pe.PharmaBackend.dto.CategoriaResponseDTO;
import pe.edu.pe.PharmaBackend.dto.ClienteResponseDTO;
import pe.edu.pe.PharmaBackend.entity.Categoria;
import pe.edu.pe.PharmaBackend.exception.RecursoNoEncontradoException;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.repository.CategoriaRepository;
import pe.edu.pe.PharmaBackend.service.service.CategoriaService;

@Service
public class CategoriaServiceImpl implements CategoriaService {

    private static final Logger LOG = LoggerFactory.getLogger(CategoriaServiceImpl.class);

    private final CategoriaRepository categoriaRepository;

    public CategoriaServiceImpl(CategoriaRepository categoriaRepository) {
        this.categoriaRepository = categoriaRepository;
    }

    @Override
    @Transactional
    public CategoriaResponseDTO create(CategoriaRequestDTO t) {
        String nombre = t.getNombre().trim();
        if (categoriaRepository.existsByNombreIgnoreCase(nombre)) {
            throw new ReglaNegocioException("El nombre de categoría ya existe en el sistema: " + nombre);
        }
        Categoria categoria = new Categoria();
        categoria.setNombre(nombre);
        categoria.setDescripcion(t.getDescripcion());
        categoria.setEstado(t.getEstado());
        Categoria catCreada = categoriaRepository.save(categoria);
        LOG.info("Categoria creada con id={}", catCreada.getId());
        return convertirResponse(catCreada);
    }

    @Override
    @Transactional
    public CategoriaResponseDTO update(Long id, CategoriaRequestDTO t) {
        Categoria categoria = categoriaRepository.findById(id).orElseThrow(() ->
                new RecursoNoEncontradoException("Categoria no encontrada con el id: " + id));

        String nombre = t.getNombre().trim();
        if (categoriaRepository.existsByNombreIgnoreCaseAndIdNot(nombre, id)) {
            throw new ReglaNegocioException("El nombre de categoría ya existe en el sistema: " + nombre);
        }

        categoria.setNombre(nombre);
        categoria.setDescripcion(t.getDescripcion());
        categoria.setEstado(t.getEstado());
        Categoria catActualizada = categoriaRepository.save(categoria);
        LOG.info("Categoria id={} actualizada", catActualizada.getId());
        return convertirResponse(catActualizada);
    }

    @Override
    @Transactional(readOnly = true)
    public ClienteResponseDTO read(Long id) {
        return categoriaRepository.findById(id).map(this::convertirResponse);
    }

    @Override
    @Transactional
    public void delete(Long id) {
        Categoria categoria = categoriaRepository.findById(id).orElseThrow(() ->
                new RecursoNoEncontradoException("Categoria no encontrada con el id: " + id));
        categoriaRepository.delete(categoria);
        LOG.info("Categoria id={} eliminada", id);
    }

    @Override
    @Transactional(readOnly = true)
    public Iterable<CategoriaResponseDTO> readAll() {
        return categoriaRepository.findAll().stream().map(this::convertirResponse).toList();
    }

    private CategoriaResponseDTO convertirResponse(Categoria categoria) {
        return new CategoriaResponseDTO(
                categoria.getId(),
                categoria.getNombre(),
                categoria.getDescripcion(),
                categoria.getEstado(),
                categoria.getFechaCreacion(),
                categoria.getFechaModificacion()
        );
    }
}