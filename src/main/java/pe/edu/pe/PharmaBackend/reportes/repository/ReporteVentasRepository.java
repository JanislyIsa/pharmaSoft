package pe.edu.pe.PharmaBackend.reportes.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import pe.edu.pe.PharmaBackend.entity.Venta;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public interface ReporteVentasRepository extends JpaRepository<Venta, Long> {

    interface VentaPorCategoriaProjection {
        Long getCategoriaId();
        String getCategoriaNombre();
        Long getCantidadVendida();
        BigDecimal getMontoTotal();
    }

    @Query("""
            select c.id as categoriaId,
                   c.nombre as categoriaNombre,
                   sum(d.cantidad) as cantidadVendida,
                   sum(d.subtotal) as montoTotal
            from DetalleVenta d
            join d.venta v
            join d.producto p
            join p.categoria c
            where v.estado = pe.edu.pe.PharmaBackend.enums.EstadoVenta.REGISTRADA
              and (:desde is null or v.fecha >= :desde)
              and (:hastaExclusivo is null or v.fecha < :hastaExclusivo)
            group by c.id, c.nombre
            order by sum(d.subtotal) desc, c.nombre asc
            """)
    List<VentaPorCategoriaProjection> ventasPorCategoria(
            @Param("desde") LocalDateTime desde,
            @Param("hastaExclusivo") LocalDateTime hastaExclusivo);
}
