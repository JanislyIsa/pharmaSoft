package pe.edu.pe.PharmaBackend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.query.Param;
import pe.edu.pe.PharmaBackend.entity.DetalleVenta;
import org.springframework.data.jpa.repository.Query;
import pe.edu.pe.PharmaBackend.dto.reporte.VentaPorCategoriaDTO;
import pe.edu.pe.PharmaBackend.dto.reporte.ProductoMasVendidoDTO;
import java.time.LocalDateTime;
import java.util.List;

public interface DetalleVentaRepository extends JpaRepository<DetalleVenta, Long> {
    @Query("""
        select new pe.edu.pe.PharmaBackend.dto.reporte.VentaPorCategoriaDTO(
                   cat.id,
                   cat.nombre,
                   sum(d.cantidad),
                   sum(d.subtotal))
        from DetalleVenta d
        join d.venta v
        join d.producto p
        join p.categoria cat
        where v.estado = pe.edu.pe.PharmaBackend.enums.EstadoVenta.REGISTRADA
          and (:desde is null or v.fecha >= :desde)
          and (:hasta is null or v.fecha <= :hasta)
        group by cat.id, cat.nombre
        order by sum(d.subtotal) desc
        """)
    List<VentaPorCategoriaDTO> reporteVentasPorCategoria(
            @Param("desde") LocalDateTime desde,
            @Param("hasta") LocalDateTime hasta);


    @Query("""
        select new pe.edu.pe.PharmaBackend.dto.reporte.ProductoMasVendidoDTO(
                   p.id,
                   p.nombre,
                   cat.nombre,
                   sum(d.cantidad),
                   sum(d.subtotal))
        from DetalleVenta d
        join d.venta v
        join d.producto p
        join p.categoria cat
        where v.estado = pe.edu.pe.PharmaBackend.enums.EstadoVenta.REGISTRADA
          and (:desde is null or v.fecha >= :desde)
          and (:hasta is null or v.fecha <= :hasta)
        group by p.id, p.nombre, cat.nombre
        order by sum(d.cantidad) desc
        """)
    List<ProductoMasVendidoDTO> reporteProductosMasVendidos(
            @Param("desde") LocalDateTime desde,
            @Param("hasta") LocalDateTime hasta);
}