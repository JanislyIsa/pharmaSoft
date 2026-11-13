package pe.edu.pe.PharmaBackend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.pe.PharmaBackend.entity.Producto;

import java.util.List;

public interface ProductoRepository extends JpaRepository<Producto, Long> {

    @org.springframework.data.jpa.repository.Query("select p from Producto p where p.estado=true and p.stock>0 and upper(p.nombre) like upper(concat('%',:texto,'%'))")
    org.springframework.data.domain.Page<Producto> buscarVendibles(@org.springframework.data.repository.query.Param("texto") String texto, org.springframework.data.domain.Pageable pageable);
    boolean existsByNombreIgnoreCase(String nombre);
    boolean existsByNombreIgnoreCaseAndIdNot(String nombre, long id);

    List<Producto> findByCategoriaId(Long categoriaId);
    boolean existsByCategoriaId(Long categoriaId);
}