package pe.edu.pe.PharmaBackend.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import pe.edu.pe.PharmaBackend.entity.Venta;
import pe.edu.pe.PharmaBackend.enums.EstadoVenta;

import java.time.LocalDateTime;
import java.util.Optional;

public interface VentaRepository extends JpaRepository<Venta, Long> {

    @EntityGraph(attributePaths = {"cliente", "detalles", "detalles.producto"})
    Optional<Venta> findConDatosById(Long id);

    @EntityGraph(attributePaths = "cliente")
    @Query("""
            select v from Venta v
            where (:clienteId is null or v.cliente.id = :clienteId)
              and (:estado is null or v.estado = :estado)
              and (:desde is null or v.fecha >= :desde)
              and (:hastaExclusivo is null or v.fecha < :hastaExclusivo)
            """)
    Page<Venta> buscarFiltradas(
            @Param("clienteId") Long clienteId,
            @Param("estado") EstadoVenta estado,
            @Param("desde") LocalDateTime desde,
            @Param("hastaExclusivo") LocalDateTime hastaExclusivo,
            Pageable pageable);
}
