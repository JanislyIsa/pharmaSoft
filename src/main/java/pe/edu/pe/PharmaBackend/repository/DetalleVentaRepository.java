package pe.edu.pe.PharmaBackend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.pe.PharmaBackend.entity.DetalleVenta;

public interface DetalleVentaRepository extends JpaRepository<DetalleVenta, Long> {
}