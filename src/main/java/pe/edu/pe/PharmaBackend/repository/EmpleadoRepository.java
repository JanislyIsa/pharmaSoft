package pe.edu.pe.PharmaBackend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.pe.PharmaBackend.entity.Empleado;

public interface EmpleadoRepository extends JpaRepository<Empleado, Long> { }
