package pe.edu.pe.PharmaBackend.entity;

import jakarta.persistence.*;
import lombok.*;


@Entity
@Table(name = "roles")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
public class Rol {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, length = 30)
    private String nombre;
    @Column(length = 150)
    private String descripcion;
}