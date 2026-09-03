package pe.edu.pe.PharmaBackend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.pe.PharmaBackend.entity.Venta;

public interface VentaRepository extends JpaRepository<Venta, Long> {
}