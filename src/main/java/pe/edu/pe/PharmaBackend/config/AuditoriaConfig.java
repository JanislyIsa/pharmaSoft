package pe.edu.pe.PharmaBackend.config;
import java.util.Optional;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.AuditorAware;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import pe.edu.pe.PharmaBackend.auditoria.EventoAuditoria;
@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditor")
public class AuditoriaConfig {
 @Bean public AuditorAware<String> auditor() {
  return () -> Optional.of(EventoAuditoria.usuarioActual("sistema"));
 }
}
