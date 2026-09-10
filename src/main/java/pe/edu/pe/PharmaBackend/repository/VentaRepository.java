package pe.edu.pe.PharmaBackend.repository;

import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import pe.edu.pe.PharmaBackend.entity.Venta;
import pe.edu.pe.PharmaBackend.enums.EstadoVenta;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

public interface VentaRepository extends JpaRepository<Venta, Long> {
    @Query("""
            SELECT DISTINCT v FROM venta v 
            LEFT JOIN FETCH v.cliente c
            LEFT JOIN FETCH v.detalle d
            LEFT JOIN FETCH v.producto p
            WHERE (:clienteId IS NULL OR c.id = :clienteId) 
            AND (:estado IS NULL OR v.estado = :estado)
            AND (:desde IS NULL OR v.fecha >= :desde)
            AND (:hasta IS NULL OR v.fecha <= :hasta)
            """)
    List<Venta> buscar(
            @Param("ClienteId")Long clienteId,
            @Param("estado") EstadoVenta estado,
            @Param("desde")LocalDateTime desde,
            @Param("hasta")LocalDateTime hasta,
            Sort sort
            );

}