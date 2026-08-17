package pe.edu.pe.PharmaBackend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.pe.PharmaBackend.entity.Categoria;

public interface CategoriaRepository extends JpaRepository<Categoria, Long> {
}
